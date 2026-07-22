"""Ingest pipeline: vložení položky -> dohledání -> extrakce atributů ->
merge filter schémat -> embedding -> uložení.

Web lookup je v 1. fázi stub — text o položce se předává ručně (`raw_text`),
nebo se extrahuje jen z názvu. TODO: napojit SearXNG / search API.
"""

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from brain import llm
from brain.config import settings
from brain.db import get_session
from brain.embeddings import embed
from brain.filters import merge_attributes
from brain.models import Category, Product, ProductEmbedding

router = APIRouter()

EXTRACT_PROMPT = (
    "Jsi extrakční nástroj e-shopu. Z textu o produktu vytáhni strukturované "
    "atributy vhodné jako filtry (velikost, barva, kapacita, materiál, ...). "
    "Vrať POUZE validní JSON objekt {\"attributes\": {...}, \"description\": \"...\"}. "
    "Číselné hodnoty jako čísla, výčty jako pole řetězců, česky."
)


class IngestRequest(BaseModel):
    category_slug: str
    name: str
    price_czk: float
    image_url: str = ""
    url: str | None = None
    raw_text: str | None = None
    # Ručně zadané atributy mají přednost před extrahovanými.
    attributes: dict[str, Any] = {}


async def _lookup(req: IngestRequest) -> str:
    # TODO: web search (SearXNG na Sparku) podle názvu/EAN/URL.
    return req.raw_text or req.name


async def _extract(text: str) -> tuple[dict[str, Any], str]:
    if not settings.llm_enabled:
        return {}, text
    raw = await llm.complete(
        [
            {"role": "system", "content": EXTRACT_PROMPT},
            {"role": "user", "content": text},
        ]
    )
    try:
        start, end = raw.index("{"), raw.rindex("}") + 1
        data = json.loads(raw[start:end])
        return dict(data.get("attributes") or {}), str(data.get("description") or text)
    except (ValueError, json.JSONDecodeError):
        return {}, text


@router.post("/ingest")
async def ingest(req: IngestRequest, session: Session = Depends(get_session)):
    category = session.scalar(select(Category).where(Category.slug == req.category_slug))
    if category is None:
        raise HTTPException(404, f"Neznámá kategorie: {req.category_slug}")

    text = await _lookup(req)
    extracted, description = await _extract(text)
    attributes = {**extracted, **req.attributes}

    product = Product(
        category_id=category.id,
        name=req.name,
        description=description if description != req.name else "",
        price_czk=req.price_czk,
        image_url=req.image_url,
        attributes=attributes,
    )
    session.add(product)
    session.flush()

    merge_attributes(session, category.id, attributes, price_czk=req.price_czk)

    embed_text = " ".join(
        [req.name, product.description, *(f"{k} {v}" for k, v in attributes.items())]
    )
    session.add(ProductEmbedding(product_id=product.id, embedding=embed(embed_text)))
    session.commit()

    return {
        "id": product.id,
        "name": product.name,
        "attributes": attributes,
        "description": product.description,
    }
