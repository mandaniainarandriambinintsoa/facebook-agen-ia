"""
Operations CRUD pour le multi-tenant
"""

import uuid
from typing import Optional
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func, text, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.db.models import Tenant, TenantConfig, Product, Embedding, MessageLog, Upload


# ─── Tenants ───────────────────────────────────────────────

async def get_tenant_by_page_id(db: AsyncSession, page_id: str) -> Optional[Tenant]:
    """Trouve un tenant par son page_id Facebook"""
    result = await db.execute(
        select(Tenant).where(Tenant.page_id == page_id, Tenant.is_active == True)
    )
    return result.scalar_one_or_none()


async def get_tenant_by_id(db: AsyncSession, tenant_id: uuid.UUID) -> Optional[Tenant]:
    """Trouve un tenant par son UUID"""
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    return result.scalar_one_or_none()


async def get_tenant_by_owner(db: AsyncSession, owner_facebook_id: str) -> list[Tenant]:
    """Liste les tenants d'un owner"""
    result = await db.execute(
        select(Tenant).where(Tenant.owner_facebook_id == owner_facebook_id)
    )
    return list(result.scalars().all())


async def create_tenant(
    db: AsyncSession,
    page_id: str,
    page_name: str,
    page_access_token: str,
    owner_email: str,
    owner_facebook_id: str = None,
) -> Tenant:
    """Cree un nouveau tenant + sa config par defaut"""
    tenant = Tenant(
        page_id=page_id,
        page_name=page_name,
        page_access_token=page_access_token,
        owner_email=owner_email,
        owner_facebook_id=owner_facebook_id,
    )
    db.add(tenant)
    await db.flush()

    # Config par defaut
    config = TenantConfig(tenant_id=tenant.id)
    db.add(config)

    await db.commit()
    await db.refresh(tenant)
    logger.info(f"Tenant cree: {page_name} (page_id={page_id})")
    return tenant


async def update_tenant_token(db: AsyncSession, tenant: Tenant, new_token: str):
    """Met a jour le token d'un tenant"""
    tenant.page_access_token = new_token
    tenant.updated_at = datetime.now(timezone.utc)
    await db.commit()


# ─── Tenant Config ─────────────────────────────────────────

async def get_tenant_config(db: AsyncSession, tenant_id: uuid.UUID) -> Optional[TenantConfig]:
    """Recupere la config d'un tenant"""
    result = await db.execute(
        select(TenantConfig).where(TenantConfig.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def update_tenant_config(db: AsyncSession, tenant_id: uuid.UUID, **kwargs) -> TenantConfig:
    """Met a jour la config d'un tenant"""
    config = await get_tenant_config(db, tenant_id)
    if not config:
        config = TenantConfig(tenant_id=tenant_id, **kwargs)
        db.add(config)
    else:
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
    await db.commit()
    await db.refresh(config)
    return config


# ─── Embeddings (pgvector) ─────────────────────────────────

async def search_embeddings(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    query_vector: list[float],
    top_k: int = 5,
) -> list[tuple]:
    """Recherche vectorielle filtree par tenant (pgvector cosine)"""
    stmt = text("""
        SELECT id, content, metadata, 1 - (embedding <=> CAST(:query_vec AS vector)) AS score
        FROM embeddings
        WHERE tenant_id = CAST(:tenant_id AS uuid)
        ORDER BY embedding <=> CAST(:query_vec AS vector)
        LIMIT :top_k
    """)
    result = await db.execute(stmt, {
        "query_vec": str(query_vector),
        "tenant_id": str(tenant_id),
        "top_k": top_k,
    })
    return result.fetchall()


async def add_embeddings(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    contents: list[str],
    vectors: list[list[float]],
    metadatas: list[dict] = None,
):
    """Insere des embeddings en batch"""
    if metadatas is None:
        metadatas = [{}] * len(contents)

    for content, vector, meta in zip(contents, vectors, metadatas):
        emb = Embedding(
            tenant_id=tenant_id,
            content=content,
            embedding=vector,
            metadata_=meta,
        )
        db.add(emb)

    await db.commit()
    logger.info(f"Tenant {tenant_id}: {len(contents)} embeddings ajoutes")


async def delete_tenant_embeddings(db: AsyncSession, tenant_id: uuid.UUID):
    """Supprime tous les embeddings d'un tenant"""
    await db.execute(
        delete(Embedding).where(Embedding.tenant_id == tenant_id)
    )
    await db.commit()


async def count_embeddings(db: AsyncSession, tenant_id: uuid.UUID) -> int:
    """Compte les embeddings d'un tenant"""
    result = await db.execute(
        select(func.count(Embedding.id)).where(Embedding.tenant_id == tenant_id)
    )
    return result.scalar() or 0


# ─── Products ──────────────────────────────────────────────

async def create_products(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    products_data: list[dict],
) -> list[Product]:
    """Cree des produits en batch"""
    products = []
    for data in products_data:
        product = Product(
            tenant_id=tenant_id,
            name=data.get("name", ""),
            description=data.get("description", ""),
            price=data.get("price", ""),
            category=data.get("category", ""),
            sizes=data.get("sizes", ""),
            colors=data.get("colors", ""),
            stock_status=data.get("stock_status", "disponible"),
            image_url=data.get("image_url", None),
            metadata_=data.get("metadata", {}),
        )
        db.add(product)
        products.append(product)
    await db.commit()
    return products


async def get_products(db: AsyncSession, tenant_id: uuid.UUID) -> list[Product]:
    """Liste les produits d'un tenant"""
    result = await db.execute(
        select(Product).where(Product.tenant_id == tenant_id)
    )
    return list(result.scalars().all())


async def get_product_by_id(db: AsyncSession, product_id: uuid.UUID) -> Optional[Product]:
    """Recupere un produit par son ID"""
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    return result.scalar_one_or_none()


async def update_product(db: AsyncSession, product: Product, **kwargs) -> Product:
    """Met a jour un produit"""
    for key, value in kwargs.items():
        if hasattr(product, key):
            setattr(product, key, value)
    await db.commit()
    await db.refresh(product)
    return product


async def delete_product(db: AsyncSession, product: Product):
    """Supprime un produit"""
    await db.delete(product)
    await db.commit()


async def delete_tenant_products(db: AsyncSession, tenant_id: uuid.UUID):
    """Supprime tous les produits d'un tenant"""
    await db.execute(
        delete(Product).where(Product.tenant_id == tenant_id)
    )
    await db.commit()


async def search_products(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    query: str = None,
    category: str = None,
    limit: int = 10,
) -> list[Product]:
    """Recherche des produits par nom/description ou categorie"""
    stmt = select(Product).where(Product.tenant_id == tenant_id)

    if category:
        stmt = stmt.where(func.lower(Product.category) == category.lower())

    if query:
        search_filter = (
            func.lower(Product.name).contains(query.lower())
            | func.lower(Product.description).contains(query.lower())
        )
        stmt = stmt.where(search_filter)

    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_product_categories(db: AsyncSession, tenant_id: uuid.UUID) -> list[str]:
    """Liste les categories distinctes d'un tenant"""
    result = await db.execute(
        select(Product.category)
        .where(Product.tenant_id == tenant_id, Product.category != "", Product.category.isnot(None))
        .distinct()
    )
    return [row[0] for row in result.fetchall()]


async def count_products(db: AsyncSession, tenant_id: uuid.UUID) -> int:
    """Compte les produits d'un tenant"""
    result = await db.execute(
        select(func.count(Product.id)).where(Product.tenant_id == tenant_id)
    )
    return result.scalar() or 0


# ─── Message Logs ──────────────────────────────────────────

async def log_message(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    sender_id: str,
    message_text: str,
    response_text: str,
    confidence_level: str = "none",
    confidence_score: float = 0.0,
    channel: str = "messenger",
):
    """Enregistre un echange message/reponse"""
    log = MessageLog(
        tenant_id=tenant_id,
        sender_id=sender_id,
        message_text=message_text,
        response_text=response_text,
        confidence_level=confidence_level,
        confidence_score=confidence_score,
        channel=channel,
    )
    db.add(log)
    await db.commit()


async def get_messages(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
) -> list[MessageLog]:
    """Recupere l'historique des messages (pagine)"""
    result = await db.execute(
        select(MessageLog)
        .where(MessageLog.tenant_id == tenant_id)
        .order_by(MessageLog.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all())


async def count_messages(db: AsyncSession, tenant_id: uuid.UUID) -> int:
    """Compte les messages d'un tenant"""
    result = await db.execute(
        select(func.count(MessageLog.id)).where(MessageLog.tenant_id == tenant_id)
    )
    return result.scalar() or 0


async def count_messages_today(db: AsyncSession, tenant_id: uuid.UUID) -> int:
    """Compte les messages du jour"""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.count(MessageLog.id)).where(
            MessageLog.tenant_id == tenant_id,
            MessageLog.created_at >= today_start,
        )
    )
    return result.scalar() or 0


async def get_messages_per_day(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    days: int = 30,
) -> list[tuple]:
    """Messages par jour sur les N derniers jours"""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    stmt = text("""
        SELECT DATE(created_at) as day, COUNT(*) as count
        FROM message_logs
        WHERE tenant_id = :tenant_id AND created_at >= :since
        GROUP BY DATE(created_at)
        ORDER BY day
    """)
    result = await db.execute(stmt, {"tenant_id": str(tenant_id), "since": since})
    return result.fetchall()


async def get_avg_confidence(db: AsyncSession, tenant_id: uuid.UUID) -> float:
    """Score de confiance moyen"""
    result = await db.execute(
        select(func.avg(MessageLog.confidence_score)).where(
            MessageLog.tenant_id == tenant_id
        )
    )
    return result.scalar() or 0.0


# ─── Uploads ──────────────────────────────────────────────

async def create_upload(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    filename: str,
    row_count: int,
    status: str = "completed",
) -> Upload:
    """Enregistre un upload"""
    upload = Upload(
        tenant_id=tenant_id,
        filename=filename,
        row_count=row_count,
        status=status,
    )
    db.add(upload)
    await db.commit()
    await db.refresh(upload)
    return upload


async def get_uploads(db: AsyncSession, tenant_id: uuid.UUID) -> list[Upload]:
    """Liste les uploads d'un tenant"""
    result = await db.execute(
        select(Upload)
        .where(Upload.tenant_id == tenant_id)
        .order_by(Upload.created_at.desc())
    )
    return list(result.scalars().all())
