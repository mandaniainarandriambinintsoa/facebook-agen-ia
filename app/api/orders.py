"""
API Orders — Gestion des commandes automatiques
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db
from app.db import crud
from app.db.models import Tenant
from app.auth.dependencies import get_current_tenant

router = APIRouter(prefix="/api/tenants", tags=["Orders"])


class OrderCreate(BaseModel):
    sender_id: str
    channel: str = "messenger"
    customer_name: str = ""
    customer_phone: str = ""
    customer_address: str = ""
    items: list = []
    total_amount: str = ""
    payment_method: str = ""
    notes: str = ""


class OrderStatusUpdate(BaseModel):
    status: str  # pending, confirmed, delivered, cancelled
    notes: Optional[str] = None


@router.get("/{tenant_id}/orders")
async def get_orders(
    tenant_id: str,
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Liste les commandes du tenant"""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    orders = await crud.get_orders(db, tenant.id, status=status, limit=limit, offset=offset)
    total = await crud.count_orders(db, tenant.id, status=status)

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "orders": [
            {
                "id": str(o.id),
                "sender_id": o.sender_id,
                "customer_name": o.customer_name,
                "customer_phone": o.customer_phone,
                "customer_address": o.customer_address,
                "channel": o.channel,
                "items": o.items,
                "total_amount": o.total_amount,
                "payment_method": o.payment_method,
                "status": o.status,
                "notes": o.notes,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
            for o in orders
        ],
    }


@router.get("/{tenant_id}/orders/stats")
async def get_orders_stats(
    tenant_id: str,
    days: int = Query(30, ge=1, le=90),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Stats des commandes"""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    tid = tenant.id
    today = await crud.count_orders_today(db, tid)
    total = await crud.count_orders(db, tid)
    pending = await crud.count_orders(db, tid, status="pending")
    confirmed = await crud.count_orders(db, tid, status="confirmed")
    delivered = await crud.count_orders(db, tid, status="delivered")
    cancelled = await crud.count_orders(db, tid, status="cancelled")

    per_day = await crud.get_orders_per_day(db, tid, days=days)

    # Taux de conversion: prospects -> commandes
    total_prospects = await crud.count_prospects(db, tid)
    conversion_rate = (total / total_prospects * 100) if total_prospects > 0 else 0

    return {
        "today": today,
        "total": total,
        "by_status": {
            "pending": pending,
            "confirmed": confirmed,
            "delivered": delivered,
            "cancelled": cancelled,
        },
        "conversion_rate": round(conversion_rate, 1),
        "per_day": [
            {"date": str(row.day), "count": row.count}
            for row in per_day
        ],
    }


@router.post("/{tenant_id}/orders")
async def create_order(
    tenant_id: str,
    data: OrderCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Cree une commande manuellement"""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    order = await crud.create_order(
        db=db,
        tenant_id=tenant.id,
        sender_id=data.sender_id,
        channel=data.channel,
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        customer_address=data.customer_address,
        items=data.items,
        total_amount=data.total_amount,
        payment_method=data.payment_method,
        notes=data.notes,
    )

    return {"status": "created", "order_id": str(order.id)}


@router.put("/{tenant_id}/orders/{order_id}")
async def update_order(
    tenant_id: str,
    order_id: str,
    data: OrderStatusUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Met a jour le statut d'une commande"""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    order = await crud.update_order_status(
        db, uuid.UUID(order_id), data.status, data.notes
    )
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvee")

    return {"status": "updated", "order_id": order_id, "new_status": data.status}
