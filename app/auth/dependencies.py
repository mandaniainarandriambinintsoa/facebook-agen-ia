"""
FastAPI Dependencies pour l'authentification
"""

import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import verify_token
from app.db.database import get_db
from app.db import crud
from app.db.models import Tenant

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Decode le JWT et retourne les infos user"""
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expire",
        )
    return payload


async def get_current_tenant(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Tenant:
    """Recupere le tenant lie au JWT (via tenant_id dans le token)"""
    tenant_id = user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant non specifie dans le token",
        )
    tenant = await crud.get_tenant_by_id(db, uuid.UUID(tenant_id))
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant non trouve",
        )
    return tenant
