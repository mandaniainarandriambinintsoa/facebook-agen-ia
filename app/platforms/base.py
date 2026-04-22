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

    async def send_image(self, recipient_id: str, image_url: str, caption: str = ""):
        """Envoie une image via son URL publique. Default: fallback texte si non implemente."""
        fallback = f"{caption}\n{image_url}" if caption else image_url
        await self.send_message(recipient_id, fallback)

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

            # Fetch recent chat history for this sender (conversation memory)
            from app.db import crud
            chat_history: list[dict] = []
            try:
                recent_logs = await crud.get_messages_by_sender(db, tenant.id, sender_id, limit=4)
                # MessageLog renvoye en DESC, on repasse en chronologique
                for log in reversed(recent_logs):
                    chat_history.append({"role": "user", "content": log.message_text or ""})
                    chat_history.append({"role": "assistant", "content": log.response_text or ""})
            except Exception as e:
                logger.warning(f"Echec lecture historique sender {sender_id}: {e}")

            # Generate RAG response (avec historique pour resoudre les references implicites)
            response, confidence_level, confidence_score, top_image_url = await self._generate_rag_response_mt(
                message_text, tenant, tenant_config, db, chat_history=chat_history,
            )

            # Mode classic: reponse texte pure (pas de quick replies/boutons/catalogue)
            # Mode catalog (default): quick replies contextuels (comportement historique)
            conversation_mode = getattr(tenant_config, "conversation_mode", "catalog") if tenant_config else "catalog"
            if conversation_mode == "classic":
                await self.send_message(sender_id, response)
                # Si le top document RAG a une image pertinente, on l'envoie apres le texte.
                # On inclut "low" car en pratique les scores RAG sont dans la fourchette
                # 0.3-0.5 meme pour du matching correct (embeddings courts vs contenus longs).
                if top_image_url and confidence_level in ("high", "medium", "low"):
                    try:
                        await self.send_image(sender_id, top_image_url)
                    except Exception as e:
                        logger.error(f"Erreur envoi image (classic mode): {e}")
            else:
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
        self, query: str, tenant, tenant_config, db,
        chat_history: list[dict] | None = None,
    ) -> tuple[str, str, float, str | None]:
        """Genere une reponse RAG multi-tenant via PgVectorRetriever.

        Returns (response_text, confidence_level, confidence_score, top_image_url).
        top_image_url est l'URL image du document le plus pertinent (si presente dans
        metadata), sinon None.
        """
        from app.rag.pg_retriever import PgVectorRetriever
        from app.rag.generator import ResponseGenerator
        from app.rag.confidence import ConfidenceHandler

        retriever = PgVectorRetriever(tenant_id=tenant.id, db=db)
        generator = ResponseGenerator(
            custom_system_prompt=(tenant_config.custom_system_prompt if tenant_config else None),
            conversation_mode=(getattr(tenant_config, "conversation_mode", "catalog") if tenant_config else "catalog"),
        )
        confidence = ConfidenceHandler()

        rag_response = await confidence.process_query_async(
            query, retriever, generator, chat_history=chat_history,
        )

        logger.info(
            f"RAG {tenant.page_name} — Confiance: {rag_response.confidence_level.value} "
            f"({rag_response.confidence_score:.2f})"
        )

        top_image_url = None
        if rag_response.top_document and rag_response.top_document.metadata:
            url = rag_response.top_document.metadata.get("image_url")
            if url and isinstance(url, str) and url.startswith(("http://", "https://")):
                top_image_url = url

        return (
            rag_response.response,
            rag_response.confidence_level.value,
            rag_response.confidence_score,
            top_image_url,
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
