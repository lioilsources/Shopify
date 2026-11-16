"""Ingest pipeline: lookup -> attribute extraction -> embedding -> draft.

Every ingested product starts as a `draft` and is not public until an admin
approves it (plan 02, invariant 3). Filters grow when a product gets listed,
see brain.catalog.set_status. Re-ingest with the same `source_key` updates
the row instead of creating a duplicate.

The lookup is still a stub: text comes in as `raw_text` or just the name.
Source adapters (e.g. the image gallery) plug in at `_lookup`.
"""

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from brain import llm
from brain.auth import require_admin
from brain.catalog import upsert_product
from brain.config import settings
from brain.db import get_session
from brain.models import Category

router = APIRouter(dependencies=[Depends(require_admin)])
log = logging.getLogger(__name__)

EXTRACT_PROMPT = (
    "Jsi extrakční nástroj e-shopu. Z textu o produktu vytáhni strukturované "
    "atributy vhodné jako filtry (velikost, barva, kapacita, materiál, ...). "
    "Vrať POUZE validní JSON objekt {\"attributes\": {...}, \"description\": \"...\"}. "
    "Číselné hodnoty jako čísla, výčty jako pole řetězců, česky."
)


class IngestRequest(BaseModel):
    category_slug: str
    name: str
    price_czk: float | None = None
    image_url: str = ""
    # Stable id in the source (e.g. image sha256); makes re-ingest idempotent.
    source_key: str | None = None
    url: str | None = None
    raw_text: str | None = None
    # Given attributes (manual entry, showcase brief) win over LLM extraction.
    attributes: dict[str, Any] = {}


async def _lookup(req: IngestRequest) -> str:
    # TODO: web search (SearXNG na Sparku) podle názvu/EAN/URL.
    return req.raw_text or req.name


async def _extract(text: str) -> tuple[dict[str, Any], str]:
    if not settings.llm_enabled:
        return {}, text
    try:
        raw = await llm.complete(
            [
                {"role": "system", "content": EXTRACT_PROMPT},
                {"role": "user", "content": text},
            ]
        )
    except Exception as exc:  # LLM not running: ingest in reduced form (plan 02, §6)
        log.warning("LLM unavailable, ingest without extraction: %s", exc)
        return {}, text
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

    product, created = upsert_product(
        session,
        category_id=category.id,
        name=req.name,
        description=description if description != req.name else "",
        price_czk=req.price_czk,
        image_url=req.image_url,
        attributes=attributes,
        source_key=req.source_key,
    )
    session.commit()

    return {
        "id": product.id,
        "name": product.name,
        "attributes": attributes,
        "description": product.description,
        "status": product.status,
        "created": created,
    }
