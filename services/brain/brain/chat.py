"""Chat endpoint: RAG + streaming přes SSE.

SSE eventy:
  token    {"text": "..."}          — kousek odpovědi
  products [{id, name, price_czk, image_url, category_slug}, ...]
                                    — the web sets the gallery selection to these ids
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
from brain.rag import product_context, search_products

router = APIRouter()
log = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Jsi nákupní asistent e-shopu ChatShop. Odpovídej česky, stručně a přátelsky. "
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


def _mock_answer(query: str, products: list[Product]) -> str:
    if not products:
        return "K tomuhle dotazu jsem v obchodě nic nenašel. Zkuste to popsat jinak."
    names = ", ".join(
        f"{p.name} ({p.price_czk} Kč)" if p.price_czk is not None else p.name
        for p in products[:3]
    )
    return (
        f"Asistent teď běží bez jazykového modelu. K dotazu „{query}“ jsem našel: {names}. "
        "Výběr je níže v galerii."
    )


@router.post("/chat")
async def chat(req: ChatRequest, session: Session = Depends(get_session)):
    user_query = next(
        (m.content for m in reversed(req.messages) if m.role == "user"), ""
    )
    products = search_products(session, user_query, category_slug=req.category, limit=8)

    async def event_stream():
        yield _sse("products", _product_cards(products))
        streamed = False
        if settings.llm_enabled:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT + "\n\nProdukty:\n" + product_context(products)},
                *[m.model_dump() for m in req.messages],
            ]
            try:
                async for delta in llm.stream_chat(messages):
                    streamed = True
                    yield _sse("token", {"text": delta})
            except Exception as exc:  # gateway down or model not running on SPARK
                log.warning("LLM unavailable, answering from template: %s", exc)
        if not streamed:
            answer = _mock_answer(user_query, products)
            for i in range(0, len(answer), 12):
                yield _sse("token", {"text": answer[i : i + 12]})
                await asyncio.sleep(0.02)
        yield _sse("done", {})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
