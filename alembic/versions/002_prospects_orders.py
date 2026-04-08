"""Add prospects and orders tables

Revision ID: 002
Revises: 001
Create Date: 2026-04-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prospects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", sa.String(100), nullable=False),
        sa.Column("sender_name", sa.String(255), server_default=""),
        sa.Column("channel", sa.String(20), server_default="messenger"),
        sa.Column("trigger_keyword", sa.String(100), nullable=False),
        sa.Column("trigger_message", sa.Text, nullable=False),
        sa.Column("product_interest", sa.String(500), server_default=""),
        sa.Column("status", sa.String(20), server_default="new"),
        sa.Column("notes", sa.Text, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_prospects_tenant_status", "prospects", ["tenant_id", "status"])
    op.create_index("idx_prospects_tenant_id", "prospects", ["tenant_id"])

    op.create_table(
        "orders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", sa.String(100), nullable=False),
        sa.Column("customer_name", sa.String(255), server_default=""),
        sa.Column("customer_phone", sa.String(50), server_default=""),
        sa.Column("customer_address", sa.Text, server_default=""),
        sa.Column("channel", sa.String(20), server_default="messenger"),
        sa.Column("items", JSONB, server_default="[]"),
        sa.Column("total_amount", sa.String(100), server_default=""),
        sa.Column("payment_method", sa.String(50), server_default=""),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("notes", sa.Text, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_orders_tenant_status", "orders", ["tenant_id", "status"])
    op.create_index("idx_orders_tenant_id", "orders", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("orders")
    op.drop_table("prospects")
