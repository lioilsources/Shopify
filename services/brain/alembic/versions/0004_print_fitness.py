"""print profiles and per-image fitness

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-16

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "print_profiles",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("group_key", sa.String(32), nullable=False),
        sa.Column("label_cs", sa.String(128), nullable=False),
        sa.Column("label_en", sa.String(128), nullable=False),
        sa.Column("spec", JSONB, nullable=False),
        sa.Column("phase", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "product_fitness",
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("profile_id", sa.String(64), sa.ForeignKey("print_profiles.id", ondelete="CASCADE"), primary_key=True),
        # ok | upscale | caveat | no  (✅ ⬆ ⚠ ✖)
        sa.Column("grade", sa.String(8), nullable=False),
        sa.Column("max_long_cm", sa.Float(), nullable=True),
        sa.Column("max_short_cm", sa.Float(), nullable=True),
        sa.Column("upscale", sa.Float(), nullable=True),
        sa.Column("crop", sa.Float(), nullable=True),
        sa.Column("note", sa.Text(), nullable=False, server_default=""),
        sa.CheckConstraint("grade IN ('ok', 'upscale', 'caveat', 'no')", name="ck_fitness_grade"),
    )
    op.create_index("ix_product_fitness_profile_grade", "product_fitness", ["profile_id", "grade"])


def downgrade() -> None:
    op.drop_index("ix_product_fitness_profile_grade", table_name="product_fitness")
    op.drop_table("product_fitness")
    op.drop_table("print_profiles")
