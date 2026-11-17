"""Chat endpoint: RAG + streaming přes SSE.

SSE eventy:
  token    {"text": "..."}          — kousek odpovědi
  filters  {filters: {key: [values]}, category: slug|null, matches: [{key, label, value}],
            only: bool, total: int|null}
                                    — set filters recognised in the query (rule based, no LLM);
                                      only=true: nothing but filters, the gallery shows all matches
  products [{id, name, price_czk, image_url, category_slug}, ...]
                                    — the web sets the gallery selection to these ids
                                      (ignored by the web when filters.only)
  done     {}
"""

import asyncio
import json
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from brain import llm
from brain.config import settings
from brain.db import get_session
from brain.models import Product
from brain.query_filters import Extraction, extract_filters
from brain.rag import product_context, search_products
from brain.search import build_tsquery, filtered_products

router = APIRouter()
log = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Jsi nákupní asistent SlopMarketu, katalogu AI motivů k potisku. Odpovídej česky, stručně a přátelsky. "
    "Níže máš seznam produktů z obchodu relevantních k dotazu zákazníka. "
    "Doporuč ty, které dotazu odpovídají, zmiň název a cenu. "
    "Pokud nic neodpovídá, řekni to na rovinu a nic si nevymýšlej."
)


class ChatMessage(BaseModel):
    role: str  # user | assistant
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    # Category currently selected in the gallery; scopes the search.
    category: str | None = None


def _sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _product_cards(products: list[Product]) -> list[dict]:
    return [
        {
            "id": p.id,
            "name": p.name,
            "price_czk": float(p.price_czk) if p.price_czk is not None else None,
            "image_url": p.image_url,
            "category_slug": p.category.slug,
        }
        for p in products
    ]


def _filters_text(ext: Extraction) -> str:
    return ", ".join(f"{m.label}: {m.value}" for m in ext.matches)


def _count_cs(n: int) -> str:
    word = "položka" if n == 1 else "položky" if 2 <= n <= 4 else "položek"
    return f"{n} {word}"


def _mock_answer(
    query: str, products: list[Product], ext: Extraction, total: int | None = None
) -> str:
    """Honest search-box answer when no LLM runs: what was searched, what was found."""
    prefix = "Hledám bez asistenta (fulltext a filtry). "
    if ext.matches:
        prefix += f"Nastavil jsem filtry {_filters_text(ext)}. "
    if not products:
        return prefix + "Nic jsem nenašel, zkuste jiná slova nebo uvolněte filtry."
    if total is not None:
        return prefix + f"V galerii je {_count_cs(total)}."
    names = ", ".join(
        f"{p.name} ({p.price_czk} Kč)" if p.price_czk is not None else p.name
        for p in products[:3]
    )
    return prefix + f"K dotazu „{query}“ jsem našel: {names}. Výběr je níže v galerii."


@router.post("/chat")
async def chat(req: ChatRequest, session: Session = Depends(get_session)):
    user_query = next(
        (m.content for m in reversed(req.messages) if m.role == "user"), ""
    )
    ext = extract_filters(session, user_query, req.category)
    category = req.category or ext.category
    filters = ext.filters or None
    total: int | None = None
    only_filters = bool(ext.matches) and build_tsquery(ext.rest) is None
    if only_filters:
        products, total = filtered_products(session, category, filters, limit=8)
    else:
        text_query = ext.rest if ext.matches else user_query
        products = search_products(
            session, text_query, category_slug=category, limit=8, filters=filters
        )
        if not products and ext.matches:
            # Leftover words found nothing: show what the recognised part selects.
            products, total = filtered_products(session, category, filters, limit=8)
            only_filters = True

    async def event_stream():
        if ext.matches:
            yield _sse(
                "filters",
                {
                    "filters": ext.filters,
                    "category": ext.category,
                    "matches": [m.__dict__ for m in ext.matches],
                    "only": only_filters,
                    "total": total,
                },
            )
        yield _sse("products", _product_cards(products))
        streamed = False
        if settings.llm_enabled:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT
                 + (f"\n\nV galerii jsou nastavené filtry: {_filters_text(ext)}." if ext.matches else "")
                 + "\n\nProdukty:\n" + product_context(products)},
                *[m.model_dump() for m in req.messages],
            ]
            try:
                async for delta in llm.stream_chat(messages):
                    streamed = True
                    yield _sse("token", {"text": delta})
            except Exception as exc:  # gateway down or model not running on SPARK
                log.warning("LLM unavailable, answering from template: %s", exc)
        if not streamed:
            answer = _mock_answer(user_query, products, ext, total)
            for i in range(0, len(answer), 12):
                yield _sse("token", {"text": answer[i : i + 12]})
                await asyncio.sleep(0.02)
        yield _sse("done", {})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
