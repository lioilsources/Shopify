from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from brain.config import settings


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
    __table_args__ = (Index("ix_products_attributes", "attributes", postgresql_using="gin"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text, default="")
    price_czk: Mapped[float] = mapped_column(Numeric(12, 2))
    image_url: Mapped[str] = mapped_column(Text, default="")
    attributes: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

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

    product: Mapped[Product] = relationship(back_populates="embedding")
