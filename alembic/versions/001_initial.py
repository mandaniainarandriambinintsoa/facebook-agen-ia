"""Initial migration — multi-tenant SaaS schema

Revision ID: 001_initial
Revises:
Create Date: 2026-03-03
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Extension pgvector
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # tenants
    op.create_table(
        "tenants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("page_id", sa.String(50), unique=True, nullable=False),
        sa.Column("page_name", sa.String(255), nullable=False),
        sa.Column("page_access_token", sa.Text, nullable=False),
        sa.Column("owner_email", sa.String(255), nullable=False),
        sa.Column("owner_facebook_id", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_tenants_page_id", "tenants", ["page_id"])

    # tenant_configs
    op.create_table(
        "tenant_configs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("welcome_message", sa.Text, server_default=sa.text("'Bonjour ! Comment puis-je vous aider ?'")),
        sa.Column("bot_type", sa.String(50), server_default=sa.text("'ecommerce'")),
        sa.Column("delivery_enabled", sa.Boolean, server_default=sa.text("false")),
        sa.Column("phone_numbers", JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("custom_system_prompt", sa.Text, nullable=True),
        sa.Column("onboarding_step", sa.String(50), server_default=sa.text("'welcome'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

    # products
    op.create_table(
        "products",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, server_default=sa.text("''")),
        sa.Column("price", sa.String(100), server_default=sa.text("''")),
        sa.Column("category", sa.String(255), server_default=sa.text("''")),
        sa.Column("sizes", sa.String(255), server_default=sa.text("''")),
        sa.Column("colors", sa.String(255), server_default=sa.text("''")),
        sa.Column("stock_status", sa.String(50), server_default=sa.text("'disponible'")),
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_index("idx_products_tenant_id", "products", ["tenant_id"])

    # embeddings — raw SQL pour pgvector
    op.execute("""
        CREATE TABLE embeddings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            embedding vector(384) NOT NULL,
            metadata JSONB DEFAULT '{}'::jsonb
        )
    """)
    op.create_index("idx_embeddings_tenant_id", "embeddings", ["tenant_id"])
    op.execute("CREATE INDEX idx_embeddings_vector ON embeddings USING hnsw (embedding vector_cosine_ops)")

    # message_logs
    op.create_table(
        "message_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", sa.String(100), nullable=False),
        sa.Column("message_text", sa.Text, nullable=False),
        sa.Column("response_text", sa.Text, nullable=False),
        sa.Column("confidence_level", sa.String(20), server_default=sa.text("'none'")),
        sa.Column("confidence_score", sa.Float, server_default=sa.text("0.0")),
        sa.Column("channel", sa.String(20), server_default=sa.text("'messenger'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_message_logs_tenant_id", "message_logs", ["tenant_id"])

    # uploads
    op.create_table(
        "uploads",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("row_count", sa.Integer, server_default=sa.text("0")),
        sa.Column("status", sa.String(20), server_default=sa.text("'completed'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_uploads_tenant_id", "uploads", ["tenant_id"])


def downgrade():
    op.drop_table("uploads")
    op.drop_table("message_logs")
    op.drop_table("embeddings")
    op.drop_table("products")
    op.drop_table("tenant_configs")
    op.drop_table("tenants")
    op.execute("DROP EXTENSION IF EXISTS vector")
