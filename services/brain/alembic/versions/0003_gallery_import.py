"""gallery import: gate reasons, private source metadata, import cursor

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-16

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Why the publication gate holds a product back (see brain.gate).
    op.add_column(
        "products",
        sa.Column("gate_reasons", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
    )
    # Source facts that must not become public filters (model, prompt, tags, lineage).
    op.add_column(
        "products",
        sa.Column("source_meta", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.add_column("products", sa.Column("image_sha256", sa.String(64), nullable=True))
    op.create_index("ix_products_image_sha256", "products", ["image_sha256"])

    op.create_table(
        "import_state",
        sa.Column("source", sa.String(64), primary_key=True),
        sa.Column("cursor", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("import_state")
    op.drop_index("ix_products_image_sha256", table_name="products")
    op.drop_column("products", "image_sha256")
    op.drop_column("products", "source_meta")
    op.drop_column("products", "gate_reasons")
