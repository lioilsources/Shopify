"""Admin API: review queue of ingested drafts and publication status."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from brain.auth import require_admin
from brain.catalog import set_status
from brain.db import get_session
from brain.config import settings
from brain.gallery_import import run_import
from brain.models import STATUS_LISTED, STATUSES, Product, has_blocking_reason
from brain.storage import LocalStorage, StorageError

router = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])

MAX_BATCH = 500


def _row(p: Product) -> dict[str, Any]:
    return {
        "id": p.id,
        "category_slug": p.category.slug,
        "name": p.name,
        "description": p.description,
        "price_czk": float(p.price_czk) if p.price_czk is not None else None,
        "image_url": p.image_url,
        "attributes": p.attributes,
        "status": p.status,
        "source_key": p.source_key,
        "image_sha256": p.image_sha256,
        "demo": p.demo,
        "gate_reasons": p.gate_reasons or [],
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "reviewed_at": p.reviewed_at.isoformat() if p.reviewed_at else None,
    }


@router.get("/products")
def list_products(
    status: str = "draft",
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session),
):
    if status not in STATUSES:
        raise HTTPException(400, f"Neznámý stav: {status}")
    limit = max(1, min(limit, MAX_BATCH))
    base = select(Product).where(Product.status == status)
    total = session.scalar(select(func.count()).select_from(base.subquery()))
    rows = session.scalars(
        base.options(joinedload(Product.category)).order_by(Product.id).limit(limit).offset(offset)
    ).all()
    counts = dict(
        session.execute(select(Product.status, func.count()).group_by(Product.status)).all()
    )
    return {
        "total": total,
        "counts": {s: counts.get(s, 0) for s in STATUSES},
        "items": [_row(p) for p in rows],
    }


class StatusChange(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=MAX_BATCH)
    status: str


@router.post("/products/status")
def change_status(req: StatusChange, session: Session = Depends(get_session)):
    """Approve (listed), hide or return to draft a batch, e.g. a review sheet of 50."""
    if req.status not in STATUSES:
        raise HTTPException(400, f"Neznámý stav: {req.status}")
    products = session.scalars(select(Product).where(Product.id.in_(req.ids))).all()
    missing = sorted(set(req.ids) - {p.id for p in products})
    if missing:
        raise HTTPException(404, f"Neexistující produkty: {missing}")
    if req.status == STATUS_LISTED:
        blocked = sorted(p.id for p in products if has_blocking_reason(p))
        if blocked:
            raise HTTPException(409, f"Brána zveřejnění blokuje produkty: {blocked}")
    for product in products:
        set_status(session, product, req.status)
    session.commit()
    return {"updated": len(products), "status": req.status}


@router.post("/import/gallery")
def import_gallery(session: Session = Depends(get_session)):
    """Pull new items of the curated gallery collection as drafts (plan 05)."""
    if not settings.gallery_enabled:
        raise HTTPException(503, "Import z galerie není nastavený (GALLERY_URL, GALLERY_EXPORT_TOKEN).")
    try:
        return run_import(session)
    except Exception as exc:
        raise HTTPException(502, f"Galerie neodpověděla: {exc}") from exc


def _media_type(data: bytes) -> str:
    if data.startswith(b"\x89PNG"):
        return "image/png"
    if data.startswith(b"\xff\xd8"):
        return "image/jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return "application/octet-stream"


@router.get("/media/{sha256}")
def original(sha256: str):
    """Private original for the review sheet; public previews come with step 4."""
    try:
        data = LocalStorage().get(sha256.lower())
    except StorageError as exc:
        raise HTTPException(404, str(exc)) from exc
    return Response(data, media_type=_media_type(data), headers={"Cache-Control": "private, max-age=3600"})
