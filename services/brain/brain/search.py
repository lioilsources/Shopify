"""Hybrid product search: fulltext (always) + vectors (when embeddings work).

Fulltext runs on the generated `products.search_tsv` column ('simple' config
over unaccented text), so it works without any GPU. Vector search joins only
vectors produced by the currently configured model. Both rankings are fused
with Reciprocal Rank Fusion. Only `listed` products are ever returned.

Mock embeddings are a hash of words, i.e. a noisy copy of fulltext; in mock
mode the vector leg is skipped so results stay honest.
"""

import re
import unicodedata
from collections.abc import Sequence

from sqlalchemy import String, func, or_, select, text
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.orm import Session, joinedload

from brain.config import settings
from brain.embeddings import try_embed
from brain.models import STATUS_LISTED, Category, Product, ProductEmbedding

RRF_K = 60
_WORD = re.compile(r"\w+", re.UNICODE)


def strip_accents(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _term(word: str) -> str:
    # Crude stemming for an inflected language: drop the ending and match as prefix
    # ("liskou" -> "lisk:*" finds "liska", "tricko" -> "tric:*" finds "tricka").
    if len(word) >= 6:
        return f"{word[:-2]}:*"
    if len(word) == 5:
        return f"{word[:-1]}:*"
    return f"{word}:*"


def _keep_short(token: str) -> bool:
    # Short tokens are mostly prepositions ("s", "na", "do"), but sizes and
    # capacities matter ("M", "XL", "4TB", "42"): keep them when written in
    # upper case or containing a digit, and match them exactly.
    return token.isupper() or any(ch.isdigit() for ch in token)


def build_tsquery(query: str) -> str | None:
    """Turn free text into an OR tsquery string for to_tsquery('simple', ...)."""
    terms: list[str] = []
    for raw in _WORD.findall(strip_accents(query)):
        token = raw.strip("_")
        if not token:
            continue
        if len(token) <= 2:
            if _keep_short(token):
                terms.append(token.lower())
            continue
        terms.append(_term(token.lower()))
    terms = list(dict.fromkeys(terms))
    return " | ".join(terms) if terms else None


def rrf_fuse(rankings: Sequence[tuple[Sequence[int], float]], limit: int) -> list[int]:
    """Reciprocal Rank Fusion of several ranked id lists with weights."""
    scores: dict[int, float] = {}
    for ids, weight in rankings:
        for rank, pid in enumerate(ids):
            scores[pid] = scores.get(pid, 0.0) + weight / (RRF_K + rank + 1)
    return sorted(scores, key=lambda pid: (-scores[pid], pid))[:limit]


Filters = dict[str, list[str]] | None


def _base_ids_query(category_slug: str | None, filters: Filters = None):
    stmt = select(Product.id).where(Product.status == STATUS_LISTED)
    if category_slug:
        stmt = stmt.join(Category).where(Category.slug == category_slug)
    # Set filters, same semantics as the web BFF: scalar equal or list overlap.
    for key, values in (filters or {}).items():
        if values:
            stmt = stmt.where(
                or_(
                    Product.attributes[key].astext.in_(values),
                    Product.attributes[key].has_any(array(values, type_=String)),
                )
            )
    return stmt


def fulltext_ids(
    session: Session, query: str, category_slug: str | None, limit: int, filters: Filters = None
) -> list[int]:
    tsquery = build_tsquery(query)
    if not tsquery:
        return []
    q = func.to_tsquery(text("'simple'"), tsquery)
    stmt = (
        _base_ids_query(category_slug, filters)
        .where(Product.search_tsv.op("@@")(q))
        .order_by(func.ts_rank(Product.search_tsv, q).desc(), Product.id)
        .limit(limit)
    )
    return list(session.scalars(stmt))


def vector_ids(
    session: Session, query: str, category_slug: str | None, limit: int, filters: Filters = None
) -> list[int]:
    if not settings.embeddings_enabled:
        return []
    vec = try_embed(query)
    if vec is None:
        return []
    stmt = (
        _base_ids_query(category_slug, filters)
        .join(ProductEmbedding, ProductEmbedding.product_id == Product.id)
        .where(ProductEmbedding.model == settings.embedding_model_name)
        .order_by(ProductEmbedding.embedding.cosine_distance(vec))
        .limit(limit)
    )
    return list(session.scalars(stmt))


def _load(session: Session, ranked: list[int]) -> list[Product]:
    if not ranked:
        return []
    rows = session.scalars(
        select(Product).options(joinedload(Product.category)).where(Product.id.in_(ranked))
    ).all()
    by_id = {p.id: p for p in rows}
    return [by_id[pid] for pid in ranked if pid in by_id]


def search_products(
    session: Session,
    query: str,
    category_slug: str | None = None,
    limit: int = 5,
    filters: Filters = None,
) -> list[Product]:
    pool = limit * 4
    ranked = rrf_fuse(
        [
            (fulltext_ids(session, query, category_slug, pool, filters), 1.0),
            (vector_ids(session, query, category_slug, pool, filters), 1.0),
        ],
        limit,
    )
    return _load(session, ranked)


def filtered_products(
    session: Session, category_slug: str | None, filters: Filters, limit: int
) -> tuple[list[Product], int]:
    """Products matching filters only (no text left in the query) and their count."""
    base = _base_ids_query(category_slug, filters)
    total = session.scalar(select(func.count()).select_from(base.subquery())) or 0
    ids = list(session.scalars(base.order_by(Product.id).limit(limit)))
    return _load(session, ids), total


def search_mode() -> str:
    """Reported by /health and chat: which legs the search can use right now."""
    return "hybrid" if settings.embeddings_enabled else "fulltext"
