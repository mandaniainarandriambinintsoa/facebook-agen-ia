"""
Client Messenger — Multi-Tenant
Gestion des messages Facebook Messenger
"""

import httpx
from loguru import logger
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict

from app.config import settings


class MessengerClient:
    """
    Client pour l'API Facebook Messenger.
    Mode multi-tenant uniquement (token en parametre).
    """

    GRAPH_API_URL = "https://graph.facebook.com/v25.0"

    def __init__(self, access_token: str = None):
        self.access_token = access_token or settings.facebook_page_access_token
        self._last_user_message: Dict[str, datetime] = defaultdict(lambda: datetime.min)

    # ═══════════════════════════════════════════════════════
    # MULTI-TENANT
    # ═══════════════════════════════════════════════════════

    async def handle_message_mt(
        self,
        sender_id: str,
        message_text: str,
        tenant,
        tenant_config,
        db,
    ):
        """Traite un message en mode multi-tenant"""
        self._last_user_message[sender_id] = datetime.now()

        try:
            await self.send_typing_indicator(sender_id, True)

            # Check onboarding
            if tenant_config and tenant_config.onboarding_step != "complete":
                from app.facebook.onboarding import OnboardingFlow
                onboarding = OnboardingFlow(self, tenant, tenant_config, db)
                await onboarding.handle_message(sender_id, message_text)
                return

            # Generate RAG response via pgvector
            response, confidence_level, confidence_score = await self._generate_rag_response_mt(
                message_text, tenant, tenant_config, db
            )

            await self.send_message(sender_id, response)

            # Log the message
            from app.db import crud
            try:
                await crud.log_message(
                    db=db,
                    tenant_id=tenant.id,
                    sender_id=sender_id,
                    message_text=message_text,
                    response_text=response,
                    confidence_level=confidence_level,
                    confidence_score=confidence_score,
                    channel="messenger",
                )
            except Exception as e:
                logger.error(f"Erreur log message: {e}")

        except Exception as e:
            logger.error(f"Erreur traitement message MT: {e}")
            await self.send_message(
                sender_id,
                "Desolee, je rencontre un probleme technique. Reessayez dans quelques instants."
            )
        finally:
            await self.send_typing_indicator(sender_id, False)

    async def _generate_rag_response_mt(
        self, query: str, tenant, tenant_config, db
    ) -> tuple[str, str, float]:
        """
        Genere une reponse RAG multi-tenant via PgVectorRetriever.
        Retourne (response_text, confidence_level, confidence_score).
        """
        from app.rag.pg_retriever import PgVectorRetriever
        from app.rag.generator import ResponseGenerator
        from app.rag.confidence import ConfidenceHandler

        retriever = PgVectorRetriever(tenant_id=tenant.id, db=db)
        generator = ResponseGenerator(custom_system_prompt=(
            tenant_config.custom_system_prompt if tenant_config else None
        ))
        confidence = ConfidenceHandler()

        rag_response = await confidence.process_query_async(query, retriever, generator)

        logger.info(
            f"[MT] RAG {tenant.page_name} — Confiance: {rag_response.confidence_level.value} "
            f"({rag_response.confidence_score:.2f})"
        )

        return (
            rag_response.response,
            rag_response.confidence_level.value,
            rag_response.confidence_score,
        )

    # ═══════════════════════════════════════════════════════
    # SHARED methods
    # ═══════════════════════════════════════════════════════

    async def send_message(self, recipient_id: str, text: str):
        """Envoie un message texte"""
        if not self.access_token:
            logger.warning("Token d'acces non configure, message non envoye")
            return

        url = f"{self.GRAPH_API_URL}/me/messages"
        params = {"access_token": self.access_token}
        messages = self._split_long_message(text, max_length=2000)

        async with httpx.AsyncClient() as client:
            for msg in messages:
                payload = {
                    "recipient": {"id": recipient_id},
                    "message": {"text": msg},
                    "messaging_type": "RESPONSE"
                }
                try:
                    response = await client.post(url, params=params, json=payload)
                    if response.status_code != 200:
                        logger.error(f"Facebook API erreur {response.status_code}: {response.text}")
                    response.raise_for_status()
                    logger.debug(f"Message envoye a {recipient_id}")
                except httpx.HTTPError as e:
                    logger.error(f"Erreur envoi message: {e}")
                    raise

    async def send_message_with_buttons(
        self,
        recipient_id: str,
        text: str,
        buttons: List[Dict[str, str]]
    ):
        """Envoie un message avec des boutons"""
        if not self.access_token:
            return

        url = f"{self.GRAPH_API_URL}/me/messages"
        params = {"access_token": self.access_token}

        formatted_buttons = []
        for btn in buttons[:3]:
            formatted_buttons.append({
                "type": "postback",
                "title": btn["title"][:20],
                "payload": btn["payload"]
            })

        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": text[:640],
                        "buttons": formatted_buttons
                    }
                }
            },
            "messaging_type": "RESPONSE"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, params=params, json=payload)
                response.raise_for_status()
            except httpx.HTTPError as e:
                logger.error(f"Erreur envoi message avec boutons: {e}")

    async def send_typing_indicator(self, recipient_id: str, is_typing: bool):
        """Envoie l'indicateur de frappe"""
        if not self.access_token:
            return

        url = f"{self.GRAPH_API_URL}/me/messages"
        params = {"access_token": self.access_token}
        payload = {
            "recipient": {"id": recipient_id},
            "sender_action": "typing_on" if is_typing else "typing_off"
        }

        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, params=params, json=payload)
            except httpx.HTTPError:
                pass

    def _split_long_message(self, text: str, max_length: int = 2000) -> List[str]:
        """Divise un message long en plusieurs parties"""
        if len(text) <= max_length:
            return [text]

        messages = []
        current = ""
        for line in text.split("\n"):
            if len(current) + len(line) + 1 <= max_length:
                current += ("\n" if current else "") + line
            else:
                if current:
                    messages.append(current)
                current = line
        if current:
            messages.append(current)
        return messages
