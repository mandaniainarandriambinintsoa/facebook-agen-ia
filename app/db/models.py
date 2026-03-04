"""
Modeles ORM SQLAlchemy
6 tables pour le multi-tenant SaaS
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Text, Boolean, Float, Integer, ForeignKey, DateTime, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.db.database import Base


class Tenant(Base):
    """Un tenant = une page Facebook connectee"""
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id = Column(String(50), unique=True, nullable=False, index=True)
    page_name = Column(String(255), nullable=False)
    page_access_token = Column(Text, nullable=False)
    owner_email = Column(String(255), nullable=False)
    owner_facebook_id = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relations
    config = relationship("TenantConfig", back_populates="tenant", uselist=False, cascade="all, delete-orphan")
    products = relationship("Product", back_populates="tenant", cascade="all, delete-orphan")
    embeddings = relationship("Embedding", back_populates="tenant", cascade="all, delete-orphan")
    message_logs = relationship("MessageLog", back_populates="tenant", cascade="all, delete-orphan")
    uploads = relationship("Upload", back_populates="tenant", cascade="all, delete-orphan")


class TenantConfig(Base):
    """Configuration du bot par tenant"""
    __tablename__ = "tenant_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), unique=True, nullable=False)
    welcome_message = Column(Text, default="Bonjour ! Comment puis-je vous aider ?")
    bot_type = Column(String(50), default="ecommerce")
    delivery_enabled = Column(Boolean, default=False)
    phone_numbers = Column(JSONB, default=list)
    custom_system_prompt = Column(Text, nullable=True)
    onboarding_step = Column(String(50), default="welcome")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relations
    tenant = relationship("Tenant", back_populates="config")


class Product(Base):
    """Catalogue produits par tenant"""
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(500), nullable=False)
    description = Column(Text, default="")
    price = Column(String(100), default="")
    category = Column(String(255), default="")
    sizes = Column(String(255), default="")
    colors = Column(String(255), default="")
    stock_status = Column(String(50), default="disponible")
    image_url = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSONB, default=dict)

    # Relations
    tenant = relationship("Tenant", back_populates="products")


class Embedding(Base):
    """Vecteurs RAG par tenant (pgvector)"""
    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)
    metadata_ = Column("metadata", JSONB, default=dict)

    # Relations
    tenant = relationship("Tenant", back_populates="embeddings")

    __table_args__ = (
        Index("idx_embeddings_vector", embedding, postgresql_using="hnsw", postgresql_ops={"embedding": "vector_cosine_ops"}),
    )


class MessageLog(Base):
    """Historique des conversations"""
    __tablename__ = "message_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(String(100), nullable=False)
    message_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    confidence_level = Column(String(20), default="none")
    confidence_score = Column(Float, default=0.0)
    channel = Column(String(20), default="messenger")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relations
    tenant = relationship("Tenant", back_populates="message_logs")


class Upload(Base):
    """Historique des fichiers uploades"""
    __tablename__ = "uploads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    row_count = Column(Integer, default=0)
    status = Column(String(20), default="completed")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relations
    tenant = relationship("Tenant", back_populates="uploads")
