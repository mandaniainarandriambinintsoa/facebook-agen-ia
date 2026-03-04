"""
Module base de donnees
PostgreSQL + pgvector pour le multi-tenant SaaS
"""

from .database import get_db, engine, AsyncSessionLocal
from .models import Base, Tenant, TenantConfig, Product, Embedding, MessageLog, Upload

__all__ = [
    "get_db", "engine", "AsyncSessionLocal",
    "Base", "Tenant", "TenantConfig", "Product", "Embedding", "MessageLog", "Upload",
]
