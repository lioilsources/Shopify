"""Context for the chat LLM built from search results (RAG)."""

from brain.models import Product
from brain.search import search_products

__all__ = ["product_context", "search_products"]


def _price(p: Product) -> str:
    return f"{p.price_czk} Kč" if p.price_czk is not None else "cena podle provedení"


def product_context(products: list[Product]) -> str:
    lines = []
    for p in products:
        attrs = ", ".join(f"{k}: {v}" for k, v in (p.attributes or {}).items())
        lines.append(
            f"- id={p.id} | {p.name} | {_price(p)} | kategorie: {p.category.name}"
            + (f" | {attrs}" if attrs else "")
            + (f" | {p.description[:200]}" if p.description else "")
        )
    return "\n".join(lines)
