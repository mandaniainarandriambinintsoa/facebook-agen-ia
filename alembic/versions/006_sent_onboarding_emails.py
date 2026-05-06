"""Add sent_onboarding_emails table for idempotent J0-J30 cron

Revision ID: 006
Revises: 005
Create Date: 2026-05-06
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sent_onboarding_emails",
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email_key", sa.String(20), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("brevo_message_id", sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint("tenant_id", "email_key", name="pk_sent_onboarding_emails"),
    )
    op.create_index(
        "idx_sent_onboarding_tenant",
        "sent_onboarding_emails",
        ["tenant_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_sent_onboarding_tenant", table_name="sent_onboarding_emails")
    op.drop_table("sent_onboarding_emails")
