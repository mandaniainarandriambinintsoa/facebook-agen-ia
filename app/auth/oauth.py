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
        "scope": "pages_show_list,pages_messaging,pages_manage_metadata,pages_manage_engagement,pages_read_engagement",
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
    """
    pages = []
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GRAPH_API}/me/accounts", params={
            "access_token": user_token,
            "fields": "id,name,access_token,category",
        })
        resp.raise_for_status()
        data = resp.json()

        for page in data.get("data", []):
            pages.append({
                "page_id": page["id"],
                "page_name": page["name"],
                "page_access_token": page["access_token"],
                "category": page.get("category", ""),
            })

    logger.info(f"Pages trouvees: {len(pages)}")
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
