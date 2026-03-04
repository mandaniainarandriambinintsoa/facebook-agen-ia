"""
Routes OAuth + gestion des tenants
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.config import settings
from app.db.database import get_db
from app.db import crud
from app.auth import oauth
from app.auth.jwt import create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])
tenants_router = APIRouter(prefix="/api/tenants", tags=["Tenants"])


# ─── OAuth Facebook ────────────────────────────────────────

@router.get("/facebook/login")
async def facebook_login(state: str = ""):
    """Redirige vers la page d'autorisation Facebook"""
    url = await oauth.get_facebook_auth_url(state)
    return RedirectResponse(url)


@router.get("/facebook/callback")
async def facebook_callback(
    code: str = Query(...),
    state: str = Query(""),
    db: AsyncSession = Depends(get_db),
):
    """
    Callback OAuth Facebook.
    Echange le code, recupere les pages, cree les tenants, retourne un JWT.
    """
    try:
        # Echanger le code contre des tokens
        token_data = await oauth.exchange_code_for_token(code)
        user_token = token_data["user_token"]
        user_id = token_data["user_id"]
        user_email = token_data.get("user_email") or f"{user_id}@facebook.com"

        # Recuperer les pages de l'utilisateur
        pages = await oauth.get_user_pages(user_token)

        if not pages:
            raise HTTPException(status_code=400, detail="Aucune page Facebook trouvee")

        created_tenants = []
        for page in pages:
            # Verifier si tenant existe deja
            existing = await crud.get_tenant_by_page_id(db, page["page_id"])
            if existing:
                # Mettre a jour le token
                await crud.update_tenant_token(db, existing, page["page_access_token"])
                created_tenants.append(existing)
            else:
                # Creer un nouveau tenant
                tenant = await crud.create_tenant(
                    db=db,
                    page_id=page["page_id"],
                    page_name=page["page_name"],
                    page_access_token=page["page_access_token"],
                    owner_email=user_email,
                    owner_facebook_id=user_id,
                )
                created_tenants.append(tenant)

            # Abonner la page au webhook
            await oauth.subscribe_page_to_webhook(
                page["page_id"], page["page_access_token"]
            )

        # Generer un JWT (premier tenant par defaut)
        first_tenant = created_tenants[0]
        jwt_token = create_access_token({
            "sub": user_id,
            "email": user_email,
            "tenant_id": str(first_tenant.id),
        })

        # Si state contient une URL de redirect frontend
        if state and state.startswith("http"):
            return RedirectResponse(f"{state}?token={jwt_token}")

        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "tenant_id": str(first_tenant.id),
            "pages": [
                {"page_id": t.page_id, "page_name": t.page_name, "tenant_id": str(t.id)}
                for t in created_tenants
            ],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur OAuth: {str(e)}")


# ─── Tenants API ───────────────────────────────────────────

@tenants_router.get("/me")
async def get_my_tenants(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste les tenants du user courant"""
    owner_fb_id = user.get("sub")
    tenants = await crud.get_tenant_by_owner(db, owner_fb_id)
    return [
        {
            "tenant_id": str(t.id),
            "page_id": t.page_id,
            "page_name": t.page_name,
            "is_active": t.is_active,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in tenants
    ]


@tenants_router.post("/switch/{tenant_id}")
async def switch_tenant(
    tenant_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Genere un nouveau JWT pour un autre tenant du meme owner"""
    import uuid as _uuid
    tenant = await crud.get_tenant_by_id(db, _uuid.UUID(tenant_id))
    if not tenant or tenant.owner_facebook_id != user.get("sub"):
        raise HTTPException(status_code=403, detail="Acces refuse")

    token = create_access_token({
        "sub": user["sub"],
        "email": user.get("email", ""),
        "tenant_id": str(tenant.id),
    })
    return {"access_token": token, "token_type": "bearer", "tenant_id": str(tenant.id)}
