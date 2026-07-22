"""Vektorové vyhledávání produktů pro chat (RAG)."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from brain.embeddings import embed
from brain.models import Product, ProductEmbedding


def search_products(session: Session, query: str, limit: int = 5) -> list[Product]:
    query_vec = embed(query)
    stmt = (
        select(Product)
        .join(ProductEmbedding)
        .options(joinedload(Product.category))
        .order_by(ProductEmbedding.embedding.cosine_distance(query_vec))
        .limit(limit)
    )
    return list(session.scalars(stmt))


def product_context(products: list[Product]) -> str:
    lines = []
    for p in products:
        attrs = ", ".join(f"{k}: {v}" for k, v in (p.attributes or {}).items())
        lines.append(
            f"- id={p.id} | {p.name} | {p.price_czk} Kč | kategorie: {p.category.name}"
            + (f" | {attrs}" if attrs else "")
            + (f" | {p.description[:200]}" if p.description else "")
        )
    return "\n".join(lines)
