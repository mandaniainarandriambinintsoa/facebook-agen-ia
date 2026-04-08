"""
API Prospects — Detection et gestion des hot leads
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

router = APIRouter(prefix="/api/tenants", tags=["Prospects"])


class ProspectStatusUpdate(BaseModel):
    status: str  # new, contacted, converted, lost
    notes: Optional[str] = None


@router.get("/{tenant_id}/prospects")
async def get_prospects(
    tenant_id: str,
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Liste les prospects (hot leads) du tenant"""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    prospects = await crud.get_prospects(db, tenant.id, status=status, limit=limit, offset=offset)
    total = await crud.count_prospects(db, tenant.id, status=status)

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "prospects": [
            {
                "id": str(p.id),
                "sender_id": p.sender_id,
                "sender_name": p.sender_name,
                "channel": p.channel,
                "trigger_keyword": p.trigger_keyword,
                "trigger_message": p.trigger_message,
                "product_interest": p.product_interest,
                "status": p.status,
                "notes": p.notes,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in prospects
        ],
    }


@router.get("/{tenant_id}/prospects/stats")
async def get_prospects_stats(
    tenant_id: str,
    days: int = Query(30, ge=1, le=90),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Stats des prospects"""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    tid = tenant.id
    today = await crud.count_prospects_today(db, tid)
    this_week = await crud.count_prospects_this_week(db, tid)
    total = await crud.count_prospects(db, tid)
    new_count = await crud.count_prospects(db, tid, status="new")
    contacted = await crud.count_prospects(db, tid, status="contacted")
    converted = await crud.count_prospects(db, tid, status="converted")
    lost = await crud.count_prospects(db, tid, status="lost")

    per_day = await crud.get_prospects_per_day(db, tid, days=days)

    return {
        "today": today,
        "this_week": this_week,
        "total": total,
        "by_status": {
            "new": new_count,
            "contacted": contacted,
            "converted": converted,
            "lost": lost,
        },
        "per_day": [
            {"date": str(row.day), "count": row.count}
            for row in per_day
        ],
    }


@router.put("/{tenant_id}/prospects/{prospect_id}")
async def update_prospect(
    tenant_id: str,
    prospect_id: str,
    data: ProspectStatusUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Met a jour le statut d'un prospect"""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    prospect = await crud.update_prospect_status(
        db, uuid.UUID(prospect_id), data.status, data.notes
    )
    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect non trouve")

    return {"status": "updated", "prospect_id": prospect_id, "new_status": data.status}
