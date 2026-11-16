from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import CheckConstraint, Computed, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from brain.config import settings


STATUS_DRAFT = "draft"
STATUS_LISTED = "listed"
STATUS_HIDDEN = "hidden"
STATUSES = (STATUS_DRAFT, STATUS_LISTED, STATUS_HIDDEN)


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(128))

    filter_schemas: Mapped[list["FilterSchema"]] = relationship(back_populates="category")
    products: Mapped[list["Product"]] = relationship(back_populates="category")


class FilterSchema(Base):
    __tablename__ = "filter_schemas"
    __table_args__ = (Index("ix_filter_schemas_cat_attr", "category_id", "attr_key", unique=True),)

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    attr_key: Mapped[str] = mapped_column(String(64))
    label: Mapped[str] = mapped_column(String(128))
    # text | range | set | bool
    kind: Mapped[str] = mapped_column(String(16))
    # set: {"values": [...]}; range: {"min": x, "max": y, "unit": "..."}
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    category: Mapped[Category] = relationship(back_populates="filter_schemas")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        Index("ix_products_attributes", "attributes", postgresql_using="gin"),
        CheckConstraint("status IN ('draft', 'listed', 'hidden')", name="ck_products_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text, default="")
    # Optional: image catalogues price the print variant, not the product.
    price_czk: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    image_url: Mapped[str] = mapped_column(Text, default="")
    attributes: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    # draft (from ingest) -> listed (approved, public) | hidden
    status: Mapped[str] = mapped_column(String(16), default=STATUS_DRAFT, server_default=STATUS_DRAFT)
    # Idempotency key from the source (e.g. image sha256); re-ingest updates the row.
    source_key: Mapped[str | None] = mapped_column(String(128), unique=True, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    search_tsv: Mapped[Any] = mapped_column(
        TSVECTOR,
        Computed(
            "setweight(to_tsvector('simple', f_unaccent(coalesce(name, ''))), 'A') || "
            "setweight(to_tsvector('simple', f_unaccent(coalesce(description, ''))), 'B') || "
            "setweight(to_tsvector('simple', f_unaccent(coalesce(attributes::text, ''))), 'C')",
            persisted=True,
        ),
        deferred=True,
    )

    category: Mapped[Category] = relationship(back_populates="products")
    embedding: Mapped["ProductEmbedding | None"] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class ProductEmbedding(Base):
    __tablename__ = "product_embeddings"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), primary_key=True
    )
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.embedding_dim))
    # Which model produced the vector; queries only compare vectors of the same model.
    model: Mapped[str] = mapped_column(String(128), default="mock")

    product: Mapped[Product] = relationship(back_populates="embedding")
