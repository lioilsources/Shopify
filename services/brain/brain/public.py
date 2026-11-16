"""Public read endpoints for listed products (no admin token)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from brain.db import get_session
from brain.models import STATUS_LISTED, PrintProfile, Product, ProductFitness

router = APIRouter()

GRADE_ORDER = {"ok": 0, "upscale": 1, "caveat": 2, "no": 3}


@router.get("/profiles")
def profiles(session: Session = Depends(get_session)):
    rows = session.scalars(
        select(PrintProfile).where(PrintProfile.active.is_(True)).order_by(PrintProfile.phase, PrintProfile.id)
    )
    return [
        {"id": p.id, "group": p.group_key, "label_cs": p.label_cs, "label_en": p.label_en, "phase": p.phase}
        for p in rows
    ]


@router.get("/products/{product_id}/fitness")
def product_fitness(product_id: int, session: Session = Depends(get_session)):
    """Fitness table for the product detail ("Co si můžu dovolit")."""
    product = session.get(Product, product_id)
    if product is None or product.status != STATUS_LISTED:
        raise HTTPException(404, "Produkt nenalezen")
    rows = session.execute(
        select(ProductFitness, PrintProfile)
        .join(PrintProfile, PrintProfile.id == ProductFitness.profile_id)
        .where(ProductFitness.product_id == product_id, PrintProfile.active.is_(True))
    ).all()
    items = [
        {
            "profile_id": prof.id,
            "label_cs": prof.label_cs,
            "group": prof.group_key,
            "grade": fit.grade,
            "max_cm": [fit.max_short_cm, fit.max_long_cm] if fit.max_long_cm else None,
            "note": fit.note,
        }
        for fit, prof in rows
    ]
    items.sort(key=lambda r: (GRADE_ORDER[r["grade"]], r["label_cs"]))
    return {"product_id": product_id, "items": items}
