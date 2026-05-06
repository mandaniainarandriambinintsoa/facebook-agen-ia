"""Add phone column to tenants

Revision ID: 005
Revises: 004
Create Date: 2026-05-06
"""
from alembic import op
import sqlalchemy as sa


revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tenants",
        sa.Column("phone", sa.String(50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tenants", "phone")
