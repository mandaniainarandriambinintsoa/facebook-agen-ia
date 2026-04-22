"""Add conversation_mode to tenant_configs

Revision ID: 003
Revises: 002
Create Date: 2026-04-22
"""
from alembic import op
import sqlalchemy as sa


revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tenant_configs",
        sa.Column(
            "conversation_mode",
            sa.String(20),
            server_default=sa.text("'catalog'"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("tenant_configs", "conversation_mode")
