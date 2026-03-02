"""
Webhooks Facebook
Gestion des evenements entrants (messages et commentaires)
"""

from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
from loguru import logger
from typing import Any
import hmac
import hashlib

from app.config import settings
from app.facebook.messenger import MessengerClient
from app.facebook.comments import CommentsHandler


router = APIRouter()

# Clients Facebook
messenger_client = MessengerClient()
comments_handler = CommentsHandler()


@router.get("")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """
    Verification du webhook par Facebook
    Facebook envoie une requete GET pour verifier que le webhook est valide
    """
    logger.info(f"Verification webhook: mode={hub_mode}, token={hub_verify_token}")

    if hub_mode == "subscribe" and hub_verify_token == settings.facebook_verify_token:
        logger.info("Webhook verifie avec succes")
        return PlainTextResponse(content=hub_challenge)

    logger.warning("Echec verification webhook: token invalide")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("")
async def handle_webhook(request: Request):
    """
    Reception des evenements Facebook (messages et commentaires)
    """
    try:
        # Verifier la signature (optionnel mais recommande)
        body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256", "")

        if settings.facebook_app_secret and signature:
            if not verify_signature(body, signature):
                logger.warning("Signature invalide sur le webhook")
                raise HTTPException(status_code=403, detail="Invalid signature")

        # Parser le payload
        payload = await request.json()
        logger.debug(f"Webhook recu: {payload}")

        # Traiter selon le type d'objet
        object_type = payload.get("object")

        if object_type == "page":
            # Evenements de page (messages Messenger)
            await process_page_events(payload)
        elif object_type == "instagram":
            # Evenements Instagram (si configure)
            logger.info("Evenement Instagram recu (non traite)")
        else:
            logger.warning(f"Type d'objet inconnu: {object_type}")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Erreur traitement webhook: {e}")
        # Toujours retourner 200 pour eviter les retry de Facebook
        return {"status": "error", "message": str(e)}


def verify_signature(payload: bytes, signature: str) -> bool:
    """
    Verifie la signature HMAC du webhook

    Args:
        payload: Corps de la requete
        signature: Signature X-Hub-Signature-256

    Returns:
        True si la signature est valide
    """
    if not settings.facebook_app_secret:
        return True

    expected_signature = hmac.new(
        settings.facebook_app_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    actual_signature = signature.replace("sha256=", "")

    return hmac.compare_digest(expected_signature, actual_signature)


async def process_page_events(payload: dict):
    """
    Traite les evenements de page Facebook

    Args:
        payload: Payload du webhook
    """
    entries = payload.get("entry", [])

    for entry in entries:
        page_id = entry.get("id")
        logger.debug(f"Traitement evenements pour la page: {page_id}")

        # Messages Messenger
        messaging_events = entry.get("messaging", [])
        for event in messaging_events:
            await process_messaging_event(event)

        # Changements de page (commentaires)
        changes = entry.get("changes", [])
        for change in changes:
            await process_page_change(change)


async def process_messaging_event(event: dict):
    """
    Traite un evenement de messagerie Messenger

    Args:
        event: Evenement de messagerie
    """
    sender_id = event.get("sender", {}).get("id")
    recipient_id = event.get("recipient", {}).get("id")

    # Message recu
    if "message" in event:
        message = event["message"]
        message_text = message.get("text", "")

        if message_text:
            logger.info(f"Message recu de {sender_id}: {message_text[:50]}...")
            await messenger_client.handle_message(sender_id, message_text)

    # Postback (boutons)
    elif "postback" in event:
        postback = event["postback"]
        payload = postback.get("payload", "")
        logger.info(f"Postback recu de {sender_id}: {payload}")
        await messenger_client.handle_postback(sender_id, payload)

    # Reaction
    elif "reaction" in event:
        reaction = event["reaction"]
        logger.debug(f"Reaction recue de {sender_id}: {reaction}")

    # Read receipt
    elif "read" in event:
        logger.debug(f"Message lu par {sender_id}")


async def process_page_change(change: dict):
    """
    Traite un changement sur la page (commentaires, etc.)

    Args:
        change: Evenement de changement
    """
    field = change.get("field")
    value = change.get("value", {})

    if field == "feed":
        # Nouveau commentaire ou post
        item = value.get("item")

        if item == "comment":
            comment_id = value.get("comment_id")
            post_id = value.get("post_id")
            message = value.get("message", "")
            from_user = value.get("from", {})

            logger.info(f"Nouveau commentaire sur post {post_id}: {message[:50]}...")

            # Eviter de repondre a ses propres commentaires
            if from_user.get("id") != value.get("page_id"):
                await comments_handler.handle_comment(
                    comment_id=comment_id,
                    post_id=post_id,
                    message=message,
                    from_user=from_user
                )

    elif field == "mention":
        # Mention de la page
        logger.info(f"Page mentionnee: {value}")

    else:
        logger.debug(f"Changement non traite: {field}")
