"""Add auto_comment_reply to tenant_configs

Revision ID: 004
Revises: 003
Create Date: 2026-04-26
"""
from alembic import op
import sqlalchemy as sa


revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tenant_configs",
        sa.Column(
            "auto_comment_reply",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("tenant_configs", "auto_comment_reply")
