"""Catalogue writes shared by ingest, admin and seed: upsert, embedding, status."""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from brain.config import settings
from brain.embeddings import try_embed
from brain.filters import merge_attributes
from brain.models import STATUS_LISTED, Product, ProductEmbedding


def embed_text_for(product: Product) -> str:
    return " ".join(
        [
            product.name,
            product.description or "",
            *(f"{k} {v}" for k, v in (product.attributes or {}).items()),
        ]
    )


def refresh_embedding(session: Session, product: Product) -> bool:
    """(Re)compute the product vector; False when embeddings are unavailable."""
    vector = try_embed(embed_text_for(product))
    if vector is None:
        return False
    existing = session.get(ProductEmbedding, product.id)
    if existing is None:
        session.add(
            ProductEmbedding(
                product_id=product.id, embedding=vector, model=settings.embedding_model_name
            )
        )
    else:
        existing.embedding = vector
        existing.model = settings.embedding_model_name
    return True


def upsert_product(
    session: Session,
    *,
    category_id: int,
    name: str,
    description: str,
    price_czk: float | None,
    image_url: str,
    attributes: dict[str, Any],
    source_key: str | None,
) -> tuple[Product, bool]:
    """Insert a draft, or update the row with the same source_key. Returns (product, created).

    Re-ingest keeps the publication status: a listed product stays listed and
    its new attribute values are merged into the filters right away.
    """
    product = None
    if source_key:
        product = session.scalar(select(Product).where(Product.source_key == source_key))
    created = product is None
    if product is None:
        product = Product(source_key=source_key)
        session.add(product)
    product.category_id = category_id
    product.name = name
    product.description = description
    product.price_czk = price_czk
    product.image_url = image_url
    product.attributes = attributes
    session.flush()
    if product.status == STATUS_LISTED:
        merge_attributes(session, category_id, attributes, price_czk=price_czk)
    refresh_embedding(session, product)
    return product, created


def set_status(session: Session, product: Product, status: str) -> None:
    """Change publication status. Filters grow only from listed products, so that
    values of unapproved drafts never show up in the public sidebar."""
    if status == STATUS_LISTED and product.status != STATUS_LISTED:
        merge_attributes(
            session, product.category_id, product.attributes or {}, price_czk=product.price_czk
        )
    product.status = status
    product.reviewed_at = datetime.now()
