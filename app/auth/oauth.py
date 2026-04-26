"""
OAuth Facebook
Echange de code, recup pages, subscription webhook
"""

import httpx
from loguru import logger

from app.config import settings

GRAPH_API = "https://graph.facebook.com/v25.0"


async def get_facebook_auth_url(state: str = "") -> str:
    """Genere l'URL de redirection OAuth Facebook"""
    params = {
        "client_id": settings.facebook_app_id,
        "redirect_uri": settings.facebook_oauth_redirect_uri,
        "scope": "pages_show_list,pages_messaging,pages_manage_metadata,pages_read_engagement",
        "response_type": "code",
        "state": state,
    }
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    return f"https://www.facebook.com/v25.0/dialog/oauth?{qs}"


async def exchange_code_for_token(code: str) -> dict:
    """
    Echange le code OAuth contre un short-lived user token,
    puis le convertit en long-lived token.
    """
    async with httpx.AsyncClient() as client:
        # Short-lived token
        resp = await client.get(f"{GRAPH_API}/oauth/access_token", params={
            "client_id": settings.facebook_app_id,
            "client_secret": settings.facebook_app_secret,
            "redirect_uri": settings.facebook_oauth_redirect_uri,
            "code": code,
        })
        resp.raise_for_status()
        short_token = resp.json()["access_token"]

        # Long-lived token
        resp = await client.get(f"{GRAPH_API}/oauth/access_token", params={
            "grant_type": "fb_exchange_token",
            "client_id": settings.facebook_app_id,
            "client_secret": settings.facebook_app_secret,
            "fb_exchange_token": short_token,
        })
        resp.raise_for_status()
        long_token = resp.json()["access_token"]

        # Recup info user
        resp = await client.get(f"{GRAPH_API}/me", params={
            "access_token": long_token,
            "fields": "id,name,email",
        })
        resp.raise_for_status()
        user_info = resp.json()

        return {
            "user_token": long_token,
            "user_id": user_info.get("id"),
            "user_name": user_info.get("name"),
            "user_email": user_info.get("email", ""),
        }


async def get_user_pages(user_token: str) -> list[dict]:
    """
    Recupere les pages gerees par l'utilisateur avec leurs tokens permanents.

    Strategie :
    1. Endpoint standard /me/accounts (marche pour les pages owned directement)
    2. Fallback via granular_scopes + fetch individuel par page_id (necessaire
       pour la nouvelle "Login for Business" v25 ou les pages sont accessibles
       via Business Manager assets, pas directement via /me/accounts)
    """
    pages: list[dict] = []
    seen_ids: set[str] = set()

    async with httpx.AsyncClient() as client:
        # 1. Endpoint standard
        try:
            resp = await client.get(f"{GRAPH_API}/me/accounts", params={
                "access_token": user_token,
                "fields": "id,name,access_token,category",
                "limit": 100,
            })
            logger.info(
                f"[OAuth] /me/accounts status={resp.status_code} body={resp.text[:500]}"
            )
            if resp.status_code == 200:
                for page in resp.json().get("data", []):
                    if page.get("access_token") and page["id"] not in seen_ids:
                        pages.append({
                            "page_id": page["id"],
                            "page_name": page["name"],
                            "page_access_token": page["access_token"],
                            "category": page.get("category", ""),
                        })
                        seen_ids.add(page["id"])
        except Exception as e:
            logger.error(f"[OAuth] /me/accounts erreur: {e}")

        # 2. Fallback : granular_scopes (Login for Business)
        if not pages:
            try:
                resp = await client.get(f"{GRAPH_API}/me", params={
                    "access_token": user_token,
                    "fields": "id,name,granular_scopes",
                })
                logger.info(
                    f"[OAuth] /me?granular_scopes status={resp.status_code} body={resp.text[:800]}"
                )
                granular = resp.json().get("granular_scopes", []) if resp.status_code == 200 else []
                page_ids: set[str] = set()
                for entry in granular:
                    scope = entry.get("scope", "")
                    if scope.startswith("pages_"):
                        for tid in entry.get("target_ids", []) or []:
                            page_ids.add(str(tid))

                logger.info(f"[OAuth] granular page_ids={list(page_ids)}")

                for pid in page_ids:
                    if pid in seen_ids:
                        continue
                    page_resp = await client.get(f"{GRAPH_API}/{pid}", params={
                        "access_token": user_token,
                        "fields": "id,name,access_token,category",
                    })
                    if page_resp.status_code == 200:
                        page = page_resp.json()
                        if page.get("access_token"):
                            pages.append({
                                "page_id": page["id"],
                                "page_name": page.get("name", ""),
                                "page_access_token": page["access_token"],
                                "category": page.get("category", ""),
                            })
                            seen_ids.add(page["id"])
                    else:
                        logger.warning(
                            f"[OAuth] fetch page {pid} status={page_resp.status_code} body={page_resp.text[:300]}"
                        )
            except Exception as e:
                logger.error(f"[OAuth] fallback granular_scopes erreur: {e}")

    logger.info(f"[OAuth] Pages finales trouvees: {len(pages)} -> {[p['page_name'] for p in pages]}")
    return pages


async def subscribe_page_to_webhook(page_id: str, page_access_token: str) -> bool:
    """
    Abonne une page aux webhooks (messages, feed).
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_API}/{page_id}/subscribed_apps",
            params={"access_token": page_access_token},
            json={
                "subscribed_fields": ["messages", "messaging_postbacks", "feed"],
            },
        )
        if resp.status_code == 200:
            logger.info(f"Page {page_id} abonnee aux webhooks")
            return True
        else:
            logger.error(f"Erreur subscription page {page_id}: {resp.text}")
            return False
