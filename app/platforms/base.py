"""
PlatformClient — Classe de base pour tous les clients de messagerie Meta.
Chaque plateforme (Messenger, Instagram, WhatsApp) implemente les methodes d'envoi.
Le pipeline RAG est partage dans la classe de base.
"""

from abc import ABC, abstractmethod
from typing import List, Dict
from loguru import logger


class PlatformClient(ABC):
    """
    Interface commune pour les clients de messagerie.
    Toutes les plateformes implementent ces methodes.
    """

    GRAPH_API_URL = "https://graph.facebook.com/v25.0"

    def __init__(self, access_token: str):
        self.access_token = access_token

    # ─── Methodes abstraites (chaque plateforme implemente) ───

    @abstractmethod
    async def send_message(self, recipient_id: str, text: str):
        """Envoie un message texte simple"""
        ...

    @abstractmethod
    async def send_quick_replies(self, recipient_id: str, text: str, quick_replies: list[dict]):
        """Envoie un message avec des quick replies (degrade en texte si pas supporte)"""
        ...

    @abstractmethod
    async def send_generic_template(self, recipient_id: str, elements: list[dict]):
        """Envoie un carousel de produits (degrade en liste si pas supporte)"""
        ...

    @abstractmethod
    async def send_message_with_buttons(self, recipient_id: str, text: str, buttons: List[Dict[str, str]]):
        """Envoie un message avec des boutons (degrade si pas supporte)"""
        ...

    @abstractmethod
    async def send_typing_indicator(self, recipient_id: str, is_typing: bool):
        """Envoie l'indicateur de frappe (no-op si pas supporte)"""
        ...

    # ─── Pipeline RAG partage (toutes plateformes) ───

    async def handle_message_mt(
        self,
        sender_id: str,
        message_text: str,
        tenant,
        tenant_config,
        db,
        channel: str = "messenger",
    ):
        """Traite un message via le pipeline RAG — partage par toutes les plateformes"""
        try:
            await self.send_typing_indicator(sender_id, True)

            # Check onboarding (Messenger only)
            if channel == "messenger" and tenant_config and tenant_config.onboarding_step != "complete":
                from app.platforms.messenger.onboarding import OnboardingFlow
                onboarding = OnboardingFlow(self, tenant, tenant_config, db)
                await onboarding.handle_message(sender_id, message_text)
                return

            # Generate RAG response
            response, confidence_level, confidence_score = await self._generate_rag_response_mt(
                message_text, tenant, tenant_config, db
            )

            # Envoyer la reponse avec quick replies contextuels
            from app.platforms.messenger.commands import get_contextual_quick_replies
            quick_replies = get_contextual_quick_replies(confidence_level)
            await self.send_quick_replies(sender_id, response, quick_replies)

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
                    channel=channel,
                )
            except Exception as e:
                logger.error(f"Erreur log message: {e}")

            # Detect prospect intent (hot lead)
            try:
                from app.rag.prospect_detector import detect_prospect_intent
                intent = detect_prospect_intent(message_text)
                if intent:
                    await crud.create_prospect(
                        db=db,
                        tenant_id=tenant.id,
                        sender_id=sender_id,
                        channel=channel,
                        trigger_keyword=intent["keyword"],
                        trigger_message=message_text,
                        product_interest=response[:200] if response else "",
                    )
                    logger.info(f"Prospect detecte: {intent['keyword']} ({intent['category']}) - {channel}")
            except Exception as e:
                logger.error(f"Erreur detection prospect: {e}")

        except Exception as e:
            logger.error(f"Erreur traitement message ({channel}): {e}")
            await self.send_message(
                sender_id,
                "Desolee, je rencontre un probleme technique. Reessayez dans quelques instants."
            )
        finally:
            await self.send_typing_indicator(sender_id, False)

    async def _generate_rag_response_mt(
        self, query: str, tenant, tenant_config, db
    ) -> tuple[str, str, float]:
        """Genere une reponse RAG multi-tenant via PgVectorRetriever"""
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
            f"RAG {tenant.page_name} — Confiance: {rag_response.confidence_level.value} "
            f"({rag_response.confidence_score:.2f})"
        )

        return (
            rag_response.response,
            rag_response.confidence_level.value,
            rag_response.confidence_score,
        )

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
