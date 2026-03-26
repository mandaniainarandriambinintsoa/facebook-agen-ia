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
                # Mettre a jour ou creer le TenantPlatform Messenger
                tp = await crud.get_tenant_platform(db, "messenger", page["page_id"])
                if tp:
                    await crud.update_platform_token(db, tp, page["page_access_token"])
                else:
                    await crud.create_tenant_platform(
                        db, existing.id, "messenger", page["page_id"],
                        page["page_access_token"], page["page_name"],
                    )
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
                # Creer le TenantPlatform Messenger
                await crud.create_tenant_platform(
                    db, tenant.id, "messenger", page["page_id"],
                    page["page_access_token"], page["page_name"],
                )

            # Abonner la page au webhook
            await oauth.subscribe_page_to_webhook(
                page["page_id"], page["page_access_token"]
            )

            # Tenter de recuperer le compte Instagram Business lie
            try:
                import httpx
                ig_url = f"https://graph.facebook.com/v25.0/{page['page_id']}"
                ig_params = {"fields": "instagram_business_account", "access_token": page["page_access_token"]}
                async with httpx.AsyncClient() as client:
                    ig_resp = await client.get(ig_url, params=ig_params)
                    if ig_resp.status_code == 200:
                        ig_data = ig_resp.json()
                        ig_account = ig_data.get("instagram_business_account", {})
                        ig_id = ig_account.get("id")
                        if ig_id:
                            tenant_for_ig = existing or created_tenants[-1]
                            existing_ig = await crud.get_tenant_platform(db, "instagram", ig_id)
                            if not existing_ig:
                                await crud.create_tenant_platform(
                                    db, tenant_for_ig.id, "instagram", ig_id,
                                    page["page_access_token"],
                                    f"IG-{page['page_name']}",
                                )
                                logger.info(f"Instagram Business connecte: {ig_id}")
                            else:
                                await crud.update_platform_token(db, existing_ig, page["page_access_token"])
            except Exception as e:
                logger.debug(f"Pas de compte Instagram Business pour {page['page_name']}: {e}")

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


@tenants_router.get("/{tenant_id}/platforms")
async def get_platforms(
    tenant_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste les plateformes connectees du tenant"""
    import uuid as _uuid
    tenant = await crud.get_tenant_by_id(db, _uuid.UUID(tenant_id))
    if not tenant or tenant.owner_facebook_id != user.get("sub"):
        raise HTTPException(status_code=403, detail="Acces refuse")

    platforms = await crud.get_tenant_platforms(db, tenant.id)
    return [
        {
            "id": str(p.id),
            "platform": p.platform,
            "platform_id": p.platform_id,
            "platform_name": p.platform_name,
            "is_active": p.is_active,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in platforms
    ]


@tenants_router.post("/{tenant_id}/connect-whatsapp")
async def connect_whatsapp(
    tenant_id: str,
    data: dict,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Connecte un numero WhatsApp Business au tenant (config manuelle)"""
    import uuid as _uuid
    tenant = await crud.get_tenant_by_id(db, _uuid.UUID(tenant_id))
    if not tenant or tenant.owner_facebook_id != user.get("sub"):
        raise HTTPException(status_code=403, detail="Acces refuse")

    phone_number_id = data.get("phone_number_id")
    access_token = data.get("access_token")
    display_name = data.get("display_name", "WhatsApp Business")

    if not phone_number_id or not access_token:
        raise HTTPException(status_code=400, detail="phone_number_id et access_token requis")

    existing = await crud.get_tenant_platform(db, "whatsapp", phone_number_id)
    if existing:
        await crud.update_platform_token(db, existing, access_token)
        return {"status": "updated", "platform_id": phone_number_id}

    tp = await crud.create_tenant_platform(
        db, tenant.id, "whatsapp", phone_number_id,
        access_token, display_name,
    )
    return {"status": "created", "id": str(tp.id), "platform_id": phone_number_id}


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
