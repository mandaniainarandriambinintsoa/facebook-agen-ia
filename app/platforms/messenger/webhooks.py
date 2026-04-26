"""
Webhooks Multi-Plateforme Meta — Point d'entree unifie
Dispatche les evenements Facebook, Instagram et WhatsApp
"""

from fastapi import APIRouter, Request, HTTPException, Query, BackgroundTasks
from fastapi.responses import PlainTextResponse
from loguru import logger
import hmac
import hashlib

from app.config import settings

router = APIRouter()


@router.get("")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """Verification du webhook par Meta (Facebook, Instagram, WhatsApp)"""
    logger.info(f"Verification webhook: mode={hub_mode}, token={hub_verify_token}")

    if hub_mode == "subscribe" and hub_verify_token == settings.facebook_verify_token:
        logger.info("Webhook verifie avec succes")
        return PlainTextResponse(content=hub_challenge)

    logger.warning("Echec verification webhook: token invalide")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Reception des evenements Meta (Facebook, Instagram, WhatsApp)
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
            background_tasks.add_task(process_instagram_events, payload)
        elif object_type == "whatsapp_business_account":
            background_tasks.add_task(process_whatsapp_events, payload)
        else:
            logger.warning(f"Type d'objet inconnu: {object_type}")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Erreur traitement webhook: {e}")
        return {"status": "error", "message": str(e)}


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verifie la signature HMAC du webhook (meme pour les 3 plateformes Meta)"""
    if not settings.facebook_app_secret:
        return True

    expected_signature = hmac.new(
        settings.facebook_app_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    actual_signature = signature.replace("sha256=", "")
    return hmac.compare_digest(expected_signature, actual_signature)


# ═══════════════════════════════════════════════════════════════
# FACEBOOK MESSENGER
# ═══════════════════════════════════════════════════════════════

async def process_page_events(payload: dict):
    """Traite les evenements de page Facebook (Messenger + commentaires)"""
    from app.db.database import AsyncSessionLocal
    from app.db import crud
    from app.platforms.messenger.client import MessengerClient
    from app.platforms.messenger.comments import CommentsHandler

    entries = payload.get("entry", [])

    for entry in entries:
        page_id = entry.get("id")
        logger.debug(f"Traitement evenements pour la page: {page_id}")

        tenant = None
        tenant_config = None
        db = None

        if AsyncSessionLocal is not None:
            try:
                db = AsyncSessionLocal()
                # Chercher via tenant_platforms d'abord, fallback sur page_id
                tp = await crud.get_tenant_platform(db, "messenger", page_id)
                if tp:
                    tenant = await crud.get_tenant_by_id(db, tp.tenant_id)
                    tenant_config = await crud.get_tenant_config(db, tp.tenant_id)
                    logger.debug(f"Tenant trouve via platform: {tenant.page_name} ({tenant.id})")
                else:
                    # Fallback legacy
                    tenant = await crud.get_tenant_by_page_id(db, page_id)
                    if tenant:
                        tenant_config = await crud.get_tenant_config(db, tenant.id)
                        logger.debug(f"Tenant trouve (legacy): {tenant.page_name} ({tenant.id})")
            except Exception as e:
                logger.error(f"Erreur lookup tenant: {e}")

        # Messages Messenger
        messaging_events = entry.get("messaging", [])
        for event in messaging_events:
            if tenant:
                await process_messaging_event_mt(event, tenant, tenant_config, db)
            else:
                logger.warning(f"Pas de tenant pour page_id={page_id}, message ignore")

        # Commentaires
        changes = entry.get("changes", [])
        for change in changes:
            if tenant:
                await process_page_change_mt(change, tenant, tenant_config, db)
            else:
                logger.warning(f"Pas de tenant pour page_id={page_id}, changement ignore")

        if db:
            await db.close()


async def process_messaging_event_mt(event: dict, tenant, tenant_config, db):
    """Traite un message Messenger en mode multi-tenant"""
    from app.platforms.messenger.commands import CommandRouter
    from app.platforms.messenger.client import MessengerClient

    sender_id = event.get("sender", {}).get("id")
    mt_client = MessengerClient(access_token=tenant.page_access_token)
    command_router = CommandRouter(mt_client, tenant, tenant_config, db)

    # Postbacks (boutons, menu persistant, Get Started)
    if "postback" in event:
        payload = event["postback"].get("payload", "")
        logger.info(f"[Messenger] Postback de {sender_id}: {payload}")

        if payload == "GET_STARTED" and tenant_config and tenant_config.onboarding_step != "complete":
            from app.platforms.messenger.onboarding import OnboardingFlow
            onboarding = OnboardingFlow(mt_client, tenant, tenant_config, db)
            await onboarding.start()
            return

        if await command_router.handle(sender_id, payload):
            return

        await mt_client.handle_message_mt(
            sender_id=sender_id,
            message_text=payload,
            tenant=tenant,
            tenant_config=tenant_config,
            db=db,
            channel="messenger",
        )
        return

    # Messages texte
    if "message" in event:
        message = event["message"]
        message_text = message.get("text", "")

        if not message_text:
            return

        logger.info(f"[Messenger] Message de {sender_id} pour {tenant.page_name}: {message_text[:50]}...")

        quick_reply_payload = message.get("quick_reply", {}).get("payload")
        if quick_reply_payload:
            if await command_router.handle(sender_id, quick_reply_payload):
                return

        if await command_router.handle(sender_id, message_text):
            return

        await mt_client.handle_message_mt(
            sender_id=sender_id,
            message_text=message_text,
            tenant=tenant,
            tenant_config=tenant_config,
            db=db,
            channel="messenger",
        )


async def process_page_change_mt(change: dict, tenant, tenant_config, db):
    """Traite un commentaire en mode multi-tenant"""
    from app.platforms.messenger.comments import CommentsHandler

    field = change.get("field")
    value = change.get("value", {})

    if field == "feed" and value.get("item") == "comment":
        # Gate: feature opt-in par tenant
        if not (tenant_config and getattr(tenant_config, "auto_comment_reply", False)):
            logger.debug(f"[Comment] auto_comment_reply desactive pour tenant {tenant.id}, skip")
            return

        comment_id = value.get("comment_id")
        post_id = value.get("post_id")
        message = value.get("message", "")
        from_user = value.get("from", {})

        # Skip les commentaires de la page elle-meme et les commentaires sans texte
        if not message or not comment_id:
            return
        if from_user.get("id") == tenant.page_id:
            return

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


# ═══════════════════════════════════════════════════════════════
# INSTAGRAM DMs
# ═══════════════════════════════════════════════════════════════

async def process_instagram_events(payload: dict):
    """Traite les evenements Instagram (DMs)"""
    from app.db.database import AsyncSessionLocal
    from app.db import crud
    from app.platforms.instagram.client import InstagramClient
    from app.platforms.messenger.commands import CommandRouter

    entries = payload.get("entry", [])

    for entry in entries:
        ig_account_id = entry.get("id")
        logger.info(f"[Instagram] Evenement recu pour compte: {ig_account_id}")

        db = None
        try:
            db = AsyncSessionLocal()
            tp = await crud.get_tenant_platform(db, "instagram", ig_account_id)
            if not tp:
                logger.warning(f"Pas de tenant pour instagram account {ig_account_id}")
                continue

            tenant = await crud.get_tenant_by_id(db, tp.tenant_id)
            tenant_config = await crud.get_tenant_config(db, tp.tenant_id)
            client = InstagramClient(access_token=tp.access_token)

            for event in entry.get("messaging", []):
                sender_id = event.get("sender", {}).get("id")
                message = event.get("message", {})
                message_text = message.get("text", "")

                if not message_text:
                    # Message non-texte (image, sticker, etc.)
                    if message.get("attachments"):
                        await client.send_message(
                            sender_id,
                            "Je ne peux traiter que les messages texte pour le moment. "
                            "N'hesitez pas a poser votre question par ecrit !"
                        )
                    continue

                logger.info(f"[Instagram] DM de {sender_id}: {message_text[:50]}...")

                # Commandes texte
                command_router = CommandRouter(client, tenant, tenant_config, db)
                if await command_router.handle(sender_id, message_text):
                    continue

                # Pipeline RAG
                await client.handle_message_mt(
                    sender_id=sender_id,
                    message_text=message_text,
                    tenant=tenant,
                    tenant_config=tenant_config,
                    db=db,
                    channel="instagram",
                )

        except Exception as e:
            logger.error(f"Erreur traitement Instagram: {e}")
        finally:
            if db:
                await db.close()


# ═══════════════════════════════════════════════════════════════
# WHATSAPP BUSINESS
# ═══════════════════════════════════════════════════════════════

async def process_whatsapp_events(payload: dict):
    """Traite les evenements WhatsApp Business"""
    from app.db.database import AsyncSessionLocal
    from app.db import crud
    from app.platforms.whatsapp.client import WhatsAppClient
    from app.platforms.messenger.commands import CommandRouter

    entries = payload.get("entry", [])

    for entry in entries:
        for change in entry.get("changes", []):
            if change.get("field") != "messages":
                continue

            value = change.get("value", {})
            phone_number_id = value.get("metadata", {}).get("phone_number_id")

            if not phone_number_id:
                continue

            db = None
            try:
                db = AsyncSessionLocal()
                tp = await crud.get_tenant_platform(db, "whatsapp", phone_number_id)
                if not tp:
                    logger.warning(f"Pas de tenant pour whatsapp phone {phone_number_id}")
                    continue

                tenant = await crud.get_tenant_by_id(db, tp.tenant_id)
                tenant_config = await crud.get_tenant_config(db, tp.tenant_id)
                client = WhatsAppClient(
                    access_token=tp.access_token,
                    phone_number_id=phone_number_id,
                )

                for msg in value.get("messages", []):
                    sender_phone = msg.get("from")
                    msg_type = msg.get("type")

                    # Extraire le texte selon le type de message
                    if msg_type == "text":
                        message_text = msg.get("text", {}).get("body", "")
                    elif msg_type == "interactive":
                        interactive = msg.get("interactive", {})
                        if interactive.get("type") == "button_reply":
                            message_text = interactive["button_reply"].get("id", "")
                        elif interactive.get("type") == "list_reply":
                            message_text = interactive["list_reply"].get("id", "")
                        else:
                            continue
                    else:
                        # Message non-texte
                        await client.send_message(
                            sender_phone,
                            "Je ne peux traiter que les messages texte pour le moment. "
                            "N'hesitez pas a poser votre question par ecrit !"
                        )
                        continue

                    if not message_text:
                        continue

                    logger.info(f"[WhatsApp] Message de {sender_phone}: {message_text[:50]}...")

                    # Marquer comme lu
                    await client.mark_as_read(msg.get("id"))

                    # Commandes texte
                    command_router = CommandRouter(client, tenant, tenant_config, db)
                    if await command_router.handle(sender_phone, message_text):
                        continue

                    # Pipeline RAG
                    await client.handle_message_mt(
                        sender_id=sender_phone,
                        message_text=message_text,
                        tenant=tenant,
                        tenant_config=tenant_config,
                        db=db,
                        channel="whatsapp",
                    )

            except Exception as e:
                logger.error(f"Erreur traitement WhatsApp: {e}")
            finally:
                if db:
                    await db.close()
