"""
Dashboard API — stats, config, messages, knowledge
"""

import uuid
from datetime import date, datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db
from app.db import crud
from app.db.models import Tenant
from app.auth.dependencies import get_current_tenant

router = APIRouter(prefix="/api/tenants", tags=["Dashboard"])


# ─── Schemas ───────────────────────────────────────────────

class ConfigUpdate(BaseModel):
    welcome_message: Optional[str] = None
    bot_type: Optional[str] = None
    delivery_enabled: Optional[bool] = None
    phone_numbers: Optional[list] = None
    custom_system_prompt: Optional[str] = None
    conversation_mode: Optional[str] = None  # "catalog" | "classic"
    auto_comment_reply: Optional[bool] = None


# ─── Stats ─────────────────────────────────────────────────

@router.get("/{tenant_id}/stats")
async def get_stats(
    tenant_id: str,
    days: int = Query(30, ge=1, le=90),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Stats globales du tenant, filtrees sur les `days` derniers jours."""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    tid = tenant.id

    messages_period = await crud.count_messages_since(db, tid, days)
    prospects_period = await crud.count_prospects_since(db, tid, days)
    orders_period = await crud.count_orders_since(db, tid, days)
    avg_confidence = await crud.get_avg_confidence_since(db, tid, days)

    total_messages = await crud.count_messages(db, tid)
    products_count = await crud.count_products(db, tid)
    embeddings_count = await crud.count_embeddings(db, tid)
    channels = await crud.count_messages_by_channel(db, tid)
    prospects_total = await crud.count_prospects(db, tid)
    prospects_new = await crud.count_prospects(db, tid, status="new")
    orders_total = await crud.count_orders(db, tid)
    orders_pending = await crud.count_orders(db, tid, status="pending")

    conversion_rate = (orders_period / prospects_period * 100) if prospects_period > 0 else 0

    return {
        "period_days": days,
        "messages_period": messages_period,
        "prospects_period": prospects_period,
        "orders_period": orders_period,
        "avg_confidence": round(avg_confidence, 3),
        "conversion_rate": round(conversion_rate, 1),
        "orders_pending": orders_pending,
        "products_count": products_count,
        "total_messages": total_messages,
        "embeddings_count": embeddings_count,
        "page_name": tenant.page_name,
        "is_active": tenant.is_active,
        "channels": channels,
        "prospects_total": prospects_total,
        "prospects_new": prospects_new,
        "orders_total": orders_total,
    }


# ─── Messages ─────────────────────────────────────────────

@router.get("/{tenant_id}/messages")
async def get_messages(
    tenant_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Historique des messages pagine"""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    messages = await crud.get_messages(db, tenant.id, limit=limit, offset=offset)
    total = await crud.count_messages(db, tenant.id)

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "messages": [
            {
                "id": str(m.id),
                "sender_id": m.sender_id,
                "message_text": m.message_text,
                "response_text": m.response_text,
                "confidence_level": m.confidence_level,
                "confidence_score": m.confidence_score,
                "channel": m.channel,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
    }


@router.get("/{tenant_id}/messages/chart")
async def get_messages_chart(
    tenant_id: str,
    days: int = Query(30, ge=1, le=90),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Messages par jour sur les N derniers jours"""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    raw = await crud.get_messages_per_day(db, tenant.id, days=days)
    counts: dict[date, int] = {row.day: row.count for row in raw}

    today = datetime.now(timezone.utc).date()
    series = [
        {
            "date": (today - timedelta(days=i)).isoformat(),
            "count": counts.get(today - timedelta(days=i), 0),
        }
        for i in range(days - 1, -1, -1)
    ]
    return {"days": days, "data": series}


# ─── Config ───────────────────────────────────────────────

@router.get("/{tenant_id}/config")
async def get_config(
    tenant_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Recupere la config du bot"""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    config = await crud.get_tenant_config(db, tenant.id)
    if not config:
        return {"error": "Config non trouvee"}

    return {
        "welcome_message": config.welcome_message,
        "bot_type": config.bot_type,
        "delivery_enabled": config.delivery_enabled,
        "phone_numbers": config.phone_numbers,
        "custom_system_prompt": config.custom_system_prompt,
        "conversation_mode": config.conversation_mode or "catalog",
        "auto_comment_reply": bool(config.auto_comment_reply),
        "onboarding_step": config.onboarding_step,
    }


@router.put("/{tenant_id}/config")
async def update_config(
    tenant_id: str,
    data: ConfigUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Met a jour la config du bot"""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    updates = data.model_dump(exclude_unset=True)
    if "conversation_mode" in updates and updates["conversation_mode"] not in ("catalog", "classic"):
        raise HTTPException(status_code=400, detail="conversation_mode must be 'catalog' or 'classic'")
    config = await crud.update_tenant_config(db, tenant.id, **updates)

    return {
        "status": "updated",
        "welcome_message": config.welcome_message,
        "bot_type": config.bot_type,
        "delivery_enabled": config.delivery_enabled,
        "custom_system_prompt": config.custom_system_prompt,
        "conversation_mode": config.conversation_mode,
        "auto_comment_reply": bool(config.auto_comment_reply),
    }


# ─── Knowledge Stats ─────────────────────────────────────

@router.get("/{tenant_id}/knowledge-stats")
async def get_knowledge_stats(
    tenant_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Stats sur la base de connaissances"""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    embeddings_count = await crud.count_embeddings(db, tenant.id)
    products_count = await crud.count_products(db, tenant.id)
    uploads = await crud.get_uploads(db, tenant.id)

    return {
        "embeddings_count": embeddings_count,
        "products_count": products_count,
        "uploads": [
            {
                "id": str(u.id),
                "filename": u.filename,
                "row_count": u.row_count,
                "status": u.status,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in uploads
        ],
    }


@router.delete("/{tenant_id}/knowledge")
async def delete_knowledge(
    tenant_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Supprime tous les embeddings du tenant"""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    await crud.delete_tenant_embeddings(db, tenant.id)
    return {"status": "deleted"}
