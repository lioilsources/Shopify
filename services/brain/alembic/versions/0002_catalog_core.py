"""catalog core: publication status, optional price, idempotent source key,
fulltext column, embedding model name

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-16

"""
import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    # unaccent() is only STABLE; generated columns and indexes need IMMUTABLE.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION f_unaccent(text) RETURNS text
        LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT
        AS $$ SELECT public.unaccent('public.unaccent'::regdictionary, $1) $$
        """
    )

    # Existing rows were visible before, so they start as listed; new rows default to draft.
    op.add_column(
        "products",
        sa.Column("status", sa.String(16), nullable=False, server_default="listed"),
    )
    op.alter_column("products", "status", server_default="draft")
    op.create_check_constraint(
        "ck_products_status", "products", "status IN ('draft', 'listed', 'hidden')"
    )
    op.create_index("ix_products_status", "products", ["status"])

    op.add_column("products", sa.Column("source_key", sa.String(128), nullable=True))
    op.create_index("ix_products_source_key", "products", ["source_key"], unique=True)

    op.add_column("products", sa.Column("reviewed_at", sa.DateTime(), nullable=True))
    op.add_column(
        "products",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
    )

    op.alter_column("products", "price_czk", existing_type=sa.Numeric(12, 2), nullable=True)

    op.execute(
        """
        ALTER TABLE products ADD COLUMN search_tsv tsvector GENERATED ALWAYS AS (
            setweight(to_tsvector('simple', f_unaccent(coalesce(name, ''))), 'A') ||
            setweight(to_tsvector('simple', f_unaccent(coalesce(description, ''))), 'B') ||
            setweight(to_tsvector('simple', f_unaccent(coalesce(attributes::text, ''))), 'C')
        ) STORED
        """
    )
    op.create_index("ix_products_search_tsv", "products", ["search_tsv"], postgresql_using="gin")

    op.add_column(
        "product_embeddings",
        sa.Column("model", sa.String(128), nullable=False, server_default="mock"),
    )


def downgrade() -> None:
    op.drop_column("product_embeddings", "model")
    op.drop_index("ix_products_search_tsv", table_name="products")
    op.drop_column("products", "search_tsv")
    op.execute("UPDATE products SET price_czk = 0 WHERE price_czk IS NULL")
    op.alter_column("products", "price_czk", existing_type=sa.Numeric(12, 2), nullable=False)
    op.drop_column("products", "updated_at")
    op.drop_column("products", "reviewed_at")
    op.drop_index("ix_products_source_key", table_name="products")
    op.drop_column("products", "source_key")
    op.drop_index("ix_products_status", table_name="products")
    op.drop_constraint("ck_products_status", "products", type_="check")
    op.drop_column("products", "status")
    op.execute("DROP FUNCTION IF EXISTS f_unaccent(text)")
