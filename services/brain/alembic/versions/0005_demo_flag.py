"""demo flag: sample catalogue items that can be purged in one go

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-17

"""
import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("demo", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_products_demo", "products", ["demo"])


def downgrade() -> None:
    op.drop_index("ix_products_demo", table_name="products")
    op.drop_column("products", "demo")
