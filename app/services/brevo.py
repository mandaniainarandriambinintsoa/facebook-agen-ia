"""Wrapper API Brevo pour envoi d'emails transactionnels.

Usage:
    from app.services.brevo import send_template_email

    msg_id = await send_template_email(
        email_key="j0",
        to_email="client@example.com",
        to_name="Mada Shop",
        params={"prenom": "Manda", "nom_page": "Mada Shop", ...},
    )

Configuration : variables d'env BREVO_API_KEY, MAIL_FROM, MAIL_FROM_NAME.

Si BREVO_API_KEY n'est pas defini (dev local sans Brevo configure), les
fonctions log un warning et retournent None sans crash.
"""
from __future__ import annotations

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings
from app.services.brevo_templates import get_template_id, TEMPLATE_SUBJECTS


BREVO_API_BASE = "https://api.brevo.com/v3"


class BrevoError(Exception):
    """Erreur retournee par l'API Brevo."""


def _is_configured() -> bool:
    return bool(settings.brevo_api_key)


def _headers() -> dict[str, str]:
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": settings.brevo_api_key,
    }


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type((httpx.HTTPError, BrevoError)),
    reraise=True,
)
async def send_template_email(
    email_key: str,
    to_email: str,
    to_name: str | None,
    params: dict | None = None,
) -> str | None:
    """Envoie un email transactionnel via un template Brevo.

    email_key : "j0" | "j1" | "j3" | "j5" | "j7" | "j14" | "j30"
    to_email : destinataire
    to_name : nom destinataire (utilise dans le From header inbox)
    params : variables a injecter dans le template ({{params.X}})

    Retourne le messageId Brevo (utile pour tracking) ou None si non configure.
    """
    if not _is_configured():
        logger.warning(f"[brevo] BREVO_API_KEY non defini, skip envoi {email_key} -> {to_email}")
        return None

    template_id = get_template_id(email_key)
    if template_id is None:
        raise BrevoError(
            f"Template '{email_key}' non sync. "
            f"Lance d'abord : python scripts/sync_brevo_templates.py"
        )

    payload: dict = {
        "templateId": template_id,
        "to": [{"email": to_email, "name": to_name} if to_name else {"email": to_email}],
        "params": params or {},
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"{BREVO_API_BASE}/smtp/email",
            headers=_headers(),
            json=payload,
        )

    if resp.status_code >= 400:
        logger.error(f"[brevo] send {email_key} -> {to_email} failed {resp.status_code}: {resp.text}")
        raise BrevoError(f"Brevo {resp.status_code}: {resp.text}")

    data = resp.json()
    msg_id = data.get("messageId", "")
    logger.info(f"[brevo] sent {email_key} -> {to_email} (messageId={msg_id})")
    return msg_id


async def upsert_contact(
    email: str,
    attributes: dict | None = None,
) -> bool:
    """Cree ou met a jour un contact dans Brevo (utile pour segmentation marketing).

    Pas requis pour les emails transactionnels (qui peuvent etre envoyes a un email
    sans contact existant), mais utile pour suivre les utilisateurs cote Brevo.
    """
    if not _is_configured():
        logger.warning(f"[brevo] non configure, skip upsert contact {email}")
        return False

    payload = {
        "email": email,
        "attributes": attributes or {},
        "updateEnabled": True,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"{BREVO_API_BASE}/contacts",
            headers=_headers(),
            json=payload,
        )

    # 201 = created, 204 = updated, 400 si email invalide
    if resp.status_code in (201, 204):
        return True

    logger.warning(f"[brevo] upsert contact {email} {resp.status_code}: {resp.text}")
    return False


async def create_or_update_template(
    name: str,
    subject: str,
    html_content: str,
    template_id: int | None = None,
) -> int:
    """Cree (ou update si template_id fourni) un template HTML dans Brevo.

    Utilise par scripts/sync_brevo_templates.py.
    Retourne le templateId Brevo.
    """
    if not _is_configured():
        raise BrevoError("BREVO_API_KEY non defini")

    payload = {
        "templateName": name,
        "subject": subject,
        "htmlContent": html_content,
        "sender": {
            "name": settings.mail_from_name,
            "email": settings.mail_from,
        },
        "isActive": True,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        if template_id:
            # Update
            resp = await client.put(
                f"{BREVO_API_BASE}/smtp/templates/{template_id}",
                headers=_headers(),
                json=payload,
            )
            if resp.status_code != 204:
                raise BrevoError(f"Brevo update template {resp.status_code}: {resp.text}")
            return template_id
        else:
            # Create
            resp = await client.post(
                f"{BREVO_API_BASE}/smtp/templates",
                headers=_headers(),
                json=payload,
            )
            if resp.status_code != 201:
                raise BrevoError(f"Brevo create template {resp.status_code}: {resp.text}")
            return resp.json()["id"]


async def list_templates() -> list[dict]:
    """Liste tous les templates SMTP existants dans Brevo.
    Permet a sync_brevo_templates.py de detecter si un template existe deja par nom.
    """
    if not _is_configured():
        raise BrevoError("BREVO_API_KEY non defini")

    templates: list[dict] = []
    offset = 0
    page_size = 50

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            resp = await client.get(
                f"{BREVO_API_BASE}/smtp/templates",
                headers=_headers(),
                params={"limit": page_size, "offset": offset},
            )
            if resp.status_code != 200:
                raise BrevoError(f"Brevo list templates {resp.status_code}: {resp.text}")
            data = resp.json()
            batch = data.get("templates", []) or []
            templates.extend(batch)
            if len(batch) < page_size:
                break
            offset += page_size

    return templates
