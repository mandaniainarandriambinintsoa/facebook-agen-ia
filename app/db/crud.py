"""
Operations CRUD pour le multi-tenant
"""

import uuid
from typing import Optional
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func, text, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.db.models import Tenant, TenantConfig, TenantPlatform, Product, Embedding, MessageLog, Upload, Prospect, Order


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


# ─── Tenant Platforms ─────────────────────────────────────

async def get_tenant_platform(
    db: AsyncSession, platform: str, platform_id: str
) -> Optional[TenantPlatform]:
    """Trouve une connexion plateforme par type + identifiant"""
    result = await db.execute(
        select(TenantPlatform).where(
            TenantPlatform.platform == platform,
            TenantPlatform.platform_id == platform_id,
            TenantPlatform.is_active == True,
        )
    )
    return result.scalar_one_or_none()


async def create_tenant_platform(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    platform: str,
    platform_id: str,
    access_token: str,
    platform_name: str = "",
    extra_data: dict = None,
) -> TenantPlatform:
    """Ajoute une connexion plateforme a un tenant"""
    tp = TenantPlatform(
        tenant_id=tenant_id,
        platform=platform,
        platform_id=platform_id,
        access_token=access_token,
        platform_name=platform_name,
        extra_data=extra_data or {},
    )
    db.add(tp)
    await db.commit()
    await db.refresh(tp)
    logger.info(f"Tenant {tenant_id}: plateforme {platform} connectee (id={platform_id})")
    return tp


async def get_tenant_platforms(db: AsyncSession, tenant_id: uuid.UUID) -> list[TenantPlatform]:
    """Liste les plateformes connectees d'un tenant"""
    result = await db.execute(
        select(TenantPlatform).where(TenantPlatform.tenant_id == tenant_id)
    )
    return list(result.scalars().all())


async def update_platform_token(db: AsyncSession, tp: TenantPlatform, new_token: str):
    """Met a jour le token d'une plateforme"""
    tp.access_token = new_token
    tp.updated_at = datetime.now(timezone.utc)
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


async def get_messages_by_sender(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    sender_id: str,
    limit: int = 4,
) -> list[MessageLog]:
    """Derniers messages d'un sender specifique (pour l'historique conversationnel du RAG)"""
    result = await db.execute(
        select(MessageLog)
        .where(MessageLog.tenant_id == tenant_id, MessageLog.sender_id == sender_id)
        .order_by(MessageLog.created_at.desc())
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


async def count_messages_since(db: AsyncSession, tenant_id: uuid.UUID, days: int) -> int:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(func.count(MessageLog.id)).where(
            MessageLog.tenant_id == tenant_id,
            MessageLog.created_at >= since,
        )
    )
    return result.scalar() or 0


async def get_avg_confidence_since(db: AsyncSession, tenant_id: uuid.UUID, days: int) -> float:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(func.avg(MessageLog.confidence_score)).where(
            MessageLog.tenant_id == tenant_id,
            MessageLog.created_at >= since,
        )
    )
    return result.scalar() or 0.0


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


async def count_messages_by_channel(db: AsyncSession, tenant_id: uuid.UUID) -> dict:
    """Compte les messages par channel (messenger, instagram, whatsapp, comment)"""
    stmt = text("""
        SELECT channel, COUNT(*) as count
        FROM message_logs
        WHERE tenant_id = :tenant_id
        GROUP BY channel
    """)
    result = await db.execute(stmt, {"tenant_id": str(tenant_id)})
    return {row.channel: row.count for row in result.fetchall()}


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


# ─── Prospects ──────────────────────────────────────────────

async def create_prospect(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    sender_id: str,
    channel: str,
    trigger_keyword: str,
    trigger_message: str,
    product_interest: str = "",
    sender_name: str = "",
) -> Prospect:
    """Cree un nouveau prospect (hot lead)"""
    prospect = Prospect(
        tenant_id=tenant_id,
        sender_id=sender_id,
        sender_name=sender_name,
        channel=channel,
        trigger_keyword=trigger_keyword,
        trigger_message=trigger_message,
        product_interest=product_interest,
    )
    db.add(prospect)
    await db.commit()
    await db.refresh(prospect)
    logger.info(f"Prospect cree pour tenant {tenant_id}: {trigger_keyword} via {channel}")
    return prospect


async def get_prospects(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    status: str = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Prospect]:
    """Liste les prospects d'un tenant"""
    stmt = select(Prospect).where(Prospect.tenant_id == tenant_id)
    if status:
        stmt = stmt.where(Prospect.status == status)
    stmt = stmt.order_by(Prospect.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def count_prospects(db: AsyncSession, tenant_id: uuid.UUID, status: str = None) -> int:
    """Compte les prospects d'un tenant"""
    stmt = select(func.count(Prospect.id)).where(Prospect.tenant_id == tenant_id)
    if status:
        stmt = stmt.where(Prospect.status == status)
    result = await db.execute(stmt)
    return result.scalar() or 0


async def count_prospects_today(db: AsyncSession, tenant_id: uuid.UUID) -> int:
    """Compte les prospects du jour"""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.count(Prospect.id)).where(
            Prospect.tenant_id == tenant_id,
            Prospect.created_at >= today_start,
        )
    )
    return result.scalar() or 0


async def count_prospects_since(db: AsyncSession, tenant_id: uuid.UUID, days: int) -> int:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(func.count(Prospect.id)).where(
            Prospect.tenant_id == tenant_id,
            Prospect.created_at >= since,
        )
    )
    return result.scalar() or 0


async def count_prospects_this_week(db: AsyncSession, tenant_id: uuid.UUID) -> int:
    """Compte les prospects de la semaine"""
    week_start = datetime.now(timezone.utc) - timedelta(days=7)
    result = await db.execute(
        select(func.count(Prospect.id)).where(
            Prospect.tenant_id == tenant_id,
            Prospect.created_at >= week_start,
        )
    )
    return result.scalar() or 0


async def update_prospect_status(db: AsyncSession, prospect_id: uuid.UUID, status: str, notes: str = None) -> Optional[Prospect]:
    """Met a jour le statut d'un prospect"""
    result = await db.execute(select(Prospect).where(Prospect.id == prospect_id))
    prospect = result.scalar_one_or_none()
    if prospect:
        prospect.status = status
        if notes is not None:
            prospect.notes = notes
        prospect.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(prospect)
    return prospect


async def get_prospects_per_day(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    days: int = 30,
) -> list[tuple]:
    """Prospects par jour sur les N derniers jours"""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    stmt = text("""
        SELECT DATE(created_at) as day, COUNT(*) as count
        FROM prospects
        WHERE tenant_id = :tenant_id AND created_at >= :since
        GROUP BY DATE(created_at)
        ORDER BY day
    """)
    result = await db.execute(stmt, {"tenant_id": str(tenant_id), "since": since})
    return result.fetchall()


# ─── Orders ──────────────────────────────────────────────

async def create_order(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    sender_id: str,
    channel: str,
    customer_name: str = "",
    customer_phone: str = "",
    customer_address: str = "",
    items: list = None,
    total_amount: str = "",
    payment_method: str = "",
    notes: str = "",
) -> Order:
    """Cree une nouvelle commande"""
    order = Order(
        tenant_id=tenant_id,
        sender_id=sender_id,
        channel=channel,
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_address=customer_address,
        items=items or [],
        total_amount=total_amount,
        payment_method=payment_method,
        notes=notes,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    logger.info(f"Commande creee pour tenant {tenant_id}: {customer_name} via {channel}")
    return order


async def get_orders(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    status: str = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Order]:
    """Liste les commandes d'un tenant"""
    stmt = select(Order).where(Order.tenant_id == tenant_id)
    if status:
        stmt = stmt.where(Order.status == status)
    stmt = stmt.order_by(Order.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def count_orders(db: AsyncSession, tenant_id: uuid.UUID, status: str = None) -> int:
    """Compte les commandes d'un tenant"""
    stmt = select(func.count(Order.id)).where(Order.tenant_id == tenant_id)
    if status:
        stmt = stmt.where(Order.status == status)
    result = await db.execute(stmt)
    return result.scalar() or 0


async def count_orders_today(db: AsyncSession, tenant_id: uuid.UUID) -> int:
    """Compte les commandes du jour"""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.count(Order.id)).where(
            Order.tenant_id == tenant_id,
            Order.created_at >= today_start,
        )
    )
    return result.scalar() or 0


async def count_orders_since(db: AsyncSession, tenant_id: uuid.UUID, days: int) -> int:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(func.count(Order.id)).where(
            Order.tenant_id == tenant_id,
            Order.created_at >= since,
        )
    )
    return result.scalar() or 0


async def update_order_status(db: AsyncSession, order_id: uuid.UUID, status: str, notes: str = None) -> Optional[Order]:
    """Met a jour le statut d'une commande"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order:
        order.status = status
        if notes is not None:
            order.notes = notes
        order.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(order)
    return order


async def get_orders_per_day(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    days: int = 30,
) -> list[tuple]:
    """Commandes par jour sur les N derniers jours"""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    stmt = text("""
        SELECT DATE(created_at) as day, COUNT(*) as count
        FROM orders
        WHERE tenant_id = :tenant_id AND created_at >= :since
        GROUP BY DATE(created_at)
        ORDER BY day
    """)
    result = await db.execute(stmt, {"tenant_id": str(tenant_id), "since": since})
    return result.fetchall()
