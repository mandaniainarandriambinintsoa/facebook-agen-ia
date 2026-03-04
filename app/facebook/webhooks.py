"""
Webhooks Facebook — Multi-Tenant
Gestion des evenements entrants (messages et commentaires)
Lookup tenant par page_id
"""

from fastapi import APIRouter, Request, HTTPException, Query, BackgroundTasks
from fastapi.responses import PlainTextResponse
from loguru import logger
import hmac
import hashlib

from app.config import settings
from app.facebook.messenger import MessengerClient
from app.facebook.comments import CommentsHandler

router = APIRouter()


@router.get("")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """Verification du webhook par Facebook"""
    logger.info(f"Verification webhook: mode={hub_mode}, token={hub_verify_token}")

    if hub_mode == "subscribe" and hub_verify_token == settings.facebook_verify_token:
        logger.info("Webhook verifie avec succes")
        return PlainTextResponse(content=hub_challenge)

    logger.warning("Echec verification webhook: token invalide")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Reception des evenements Facebook (messages et commentaires)
    Retourne 200 immediatement, traitement en arriere-plan
    """
    try:
        body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256", "")

        if settings.facebook_app_secret and signature:
            if not verify_signature(body, signature):
                logger.warning("Signature invalide sur le webhook")
                raise HTTPException(status_code=403, detail="Invalid signature")

        payload = await request.json()
        object_type = payload.get("object")

        if object_type == "page":
            background_tasks.add_task(process_page_events, payload)
        elif object_type == "instagram":
            logger.info("Evenement Instagram recu (non traite)")
        else:
            logger.warning(f"Type d'objet inconnu: {object_type}")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Erreur traitement webhook: {e}")
        return {"status": "error", "message": str(e)}


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verifie la signature HMAC du webhook"""
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
    Traite les evenements de page Facebook.
    Multi-tenant: lookup le tenant par page_id.
    """
    from app.db.database import AsyncSessionLocal
    from app.db import crud

    entries = payload.get("entry", [])

    for entry in entries:
        page_id = entry.get("id")
        logger.debug(f"Traitement evenements pour la page: {page_id}")

        # ── Lookup tenant en BDD ──
        tenant = None
        tenant_config = None
        db = None

        if AsyncSessionLocal is not None:
            try:
                db = AsyncSessionLocal()
                tenant = await crud.get_tenant_by_page_id(db, page_id)
                if tenant:
                    tenant_config = await crud.get_tenant_config(db, tenant.id)
                    logger.debug(f"Tenant trouve: {tenant.page_name} ({tenant.id})")
            except Exception as e:
                logger.error(f"Erreur lookup tenant: {e}")

        # ── Messages Messenger ──
        messaging_events = entry.get("messaging", [])
        for event in messaging_events:
            if tenant:
                await process_messaging_event_mt(event, tenant, tenant_config, db)
            else:
                logger.warning(f"Pas de tenant pour page_id={page_id}, message ignore")

        # ── Commentaires ──
        changes = entry.get("changes", [])
        for change in changes:
            if tenant:
                await process_page_change_mt(change, tenant, tenant_config, db)
            else:
                logger.warning(f"Pas de tenant pour page_id={page_id}, changement ignore")

        # Fermer la session DB
        if db:
            await db.close()


async def process_messaging_event_mt(event: dict, tenant, tenant_config, db):
    """Traite un message Messenger en mode multi-tenant"""
    from app.facebook.commands import CommandRouter

    sender_id = event.get("sender", {}).get("id")
    mt_client = MessengerClient(access_token=tenant.page_access_token)
    command_router = CommandRouter(mt_client, tenant, tenant_config, db)

    # ── Postbacks (boutons, menu persistant, Get Started) ──
    if "postback" in event:
        payload = event["postback"].get("payload", "")
        logger.info(f"[MT] Postback de {sender_id}: {payload}")

        # Si onboarding pas termine et GET_STARTED → onboarding
        if payload == "GET_STARTED" and tenant_config and tenant_config.onboarding_step != "complete":
            from app.facebook.onboarding import OnboardingFlow
            onboarding = OnboardingFlow(mt_client, tenant, tenant_config, db)
            await onboarding.start()
            return

        # Sinon → command router
        if await command_router.handle(sender_id, payload):
            return

        # Fallback: traiter comme message texte
        await mt_client.handle_message_mt(
            sender_id=sender_id,
            message_text=payload,
            tenant=tenant,
            tenant_config=tenant_config,
            db=db,
        )
        return

    # ── Messages texte ──
    if "message" in event:
        message = event["message"]
        message_text = message.get("text", "")

        if not message_text:
            return

        logger.info(f"[MT] Message de {sender_id} pour {tenant.page_name}: {message_text[:50]}...")

        # Quick reply payload (prioritaire)
        quick_reply_payload = message.get("quick_reply", {}).get("payload")
        if quick_reply_payload:
            if await command_router.handle(sender_id, quick_reply_payload):
                return

        # Commande texte (/menu, /produits, etc.)
        if await command_router.handle(sender_id, message_text):
            return

        # Sinon → pipeline RAG normal
        await mt_client.handle_message_mt(
            sender_id=sender_id,
            message_text=message_text,
            tenant=tenant,
            tenant_config=tenant_config,
            db=db,
        )


async def process_page_change_mt(change: dict, tenant, tenant_config, db):
    """Traite un commentaire en mode multi-tenant"""
    field = change.get("field")
    value = change.get("value", {})

    if field == "feed" and value.get("item") == "comment":
        comment_id = value.get("comment_id")
        post_id = value.get("post_id")
        message = value.get("message", "")
        from_user = value.get("from", {})

        if from_user.get("id") != tenant.page_id:
            mt_handler = CommentsHandler(access_token=tenant.page_access_token)
            await mt_handler.handle_comment_mt(
                comment_id=comment_id,
                post_id=post_id,
                message=message,
                from_user=from_user,
                tenant=tenant,
                tenant_config=tenant_config,
                db=db,
            )
