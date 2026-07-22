"""Chat endpoint: RAG + streaming přes SSE.

SSE eventy:
  token    {"text": "..."}          — kousek odpovědi
  products [{id, name, price_czk, image_url, category_slug}, ...]
  done     {}
"""

import asyncio
import json

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


def _sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _product_cards(products: list[Product]) -> list[dict]:
    return [
        {
            "id": p.id,
            "name": p.name,
            "price_czk": float(p.price_czk),
            "image_url": p.image_url,
            "category_slug": p.category.slug,
        }
        for p in products
    ]


def _mock_answer(query: str, products: list[Product]) -> str:
    if not products:
        return "K tomuhle dotazu jsem v obchodě nic nenašel. Zkuste to popsat jinak."
    names = ", ".join(f"{p.name} ({p.price_czk} Kč)" for p in products[:3])
    return (
        f"(mock režim — LLM není připojeno) K dotazu „{query}“ jsem v obchodě našel: {names}. "
        "Karty produktů jsou níže, kliknutím se dostanete do galerie."
    )


@router.post("/chat")
async def chat(req: ChatRequest, session: Session = Depends(get_session)):
    user_query = next(
        (m.content for m in reversed(req.messages) if m.role == "user"), ""
    )
    products = search_products(session, user_query, limit=5)

    async def event_stream():
        yield _sse("products", _product_cards(products))
        if settings.llm_enabled:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT + "\n\nProdukty:\n" + product_context(products)},
                *[m.model_dump() for m in req.messages],
            ]
            async for delta in llm.stream_chat(messages):
                yield _sse("token", {"text": delta})
        else:
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
