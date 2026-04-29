"""
Gestionnaire de commentaires Facebook — Multi-Tenant
Pipeline : LLM classifier -> reponse publique courte (FR) + private_reply (DM)
"""

import asyncio
import random
import httpx
from loguru import logger
from typing import Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from app.config import settings


# Templates de reponse publique en FR (rotation aleatoire)
# Volontairement courts : le vrai contenu va en MP via private_reply.
PUBLIC_REPLY_TEMPLATES_FR = [
    "👋 On vous repond en prive !",
    "Bonjour 🙂 details envoyes en MP.",
    "Hello, on vous envoie tout ca en prive 📩",
    "Coucou 👋 jetez un oeil dans votre inbox !",
    "Salut, reponse en MP, a tres vite 🙂",
    "Bonjour ! On vous a ecrit en prive 📨",
]


class CommentsHandler:
    """Gestionnaire des commentaires Facebook avec classifier LLM + private reply."""

    GRAPH_API_URL = "https://graph.facebook.com/v25.0"
    PRIVATE_REPLY_MAX_LEN = 1800  # marge sous la limite Meta (~2000)
    PUBLIC_REPLY_MAX_LEN = 600

    MIN_DELAY_BETWEEN_REPLIES = 5
    MAX_REPLIES_PER_POST = 50
    MAX_REPLIES_PER_USER = 3

    def __init__(self, access_token: str = None):
        self.access_token = access_token or settings.facebook_page_access_token
        self._post_reply_count: Dict[str, list] = defaultdict(list)
        self._user_reply_count: Dict[str, list] = defaultdict(list)
        self._last_reply_time: datetime = datetime.min

    # ─── Rate-limit interne ─────────────────────────────────────

    def _can_reply(self, post_id: str, user_id: str) -> bool:
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)

        self._post_reply_count[post_id] = [
            t for t in self._post_reply_count[post_id] if t > one_hour_ago
        ]
        self._user_reply_count[user_id] = [
            t for t in self._user_reply_count[user_id] if t > one_hour_ago
        ]

        if len(self._post_reply_count[post_id]) >= self.MAX_REPLIES_PER_POST:
            return False
        if len(self._user_reply_count[user_id]) >= self.MAX_REPLIES_PER_USER:
            return False
        if (now - self._last_reply_time).total_seconds() < self.MIN_DELAY_BETWEEN_REPLIES:
            return False
        return True

    def _record_reply(self, post_id: str, user_id: str):
        now = datetime.now()
        self._post_reply_count[post_id].append(now)
        self._user_reply_count[user_id].append(now)
        self._last_reply_time = now

    # ─── Pipeline principal ─────────────────────────────────────

    async def handle_comment_mt(
        self,
        comment_id: str,
        post_id: str,
        message: str,
        from_user: Dict[str, Any],
        tenant,
        tenant_config,
        db,
    ):
        user_id = from_user.get("id", "unknown")
        user_name = from_user.get("name", "")

        if not self._can_reply(post_id, user_id):
            logger.debug(f"[Comment] Rate-limited pour user={user_id} post={post_id}")
            return

        # 1. Classifier intent
        from app.rag.comment_classifier import CommentClassifier
        classifier = CommentClassifier()
        classification = classifier.classify(message)

        logger.info(
            f"[Comment] {user_name or user_id}: \"{message[:60]}\" "
            f"-> engage={classification['engage']} intent={classification['intent']}"
        )

        if not classification["engage"]:
            return

        # 2. Generer la reponse RAG (sera envoyee en MP)
        try:
            rag_response = await self._generate_rag_response_mt(
                message, classification["intent"], tenant, tenant_config, db
            )
        except Exception as e:
            logger.error(f"[Comment] Erreur generation RAG: {e}")
            return

        # 3. Reponse publique courte (template FR) — BEST EFFORT
        # Necessite pages_manage_engagement, qui declenche un bug warning Meta
        # `Invalid Scopes: pages_read_user_content` cote OAuth admin/dev.
        # En l'absence de cette permission, on skip silencieusement et on
        # envoie uniquement le DM via private_replies (qui marche avec
        # pages_messaging seul).
        public_text = random.choice(PUBLIC_REPLY_TEMPLATES_FR)
        try:
            await asyncio.sleep(2)
            await self.reply_to_comment(comment_id, public_text, user_name)
        except Exception as e:
            logger.warning(f"[Comment] Public reply skipped (likely missing pages_manage_engagement): {e}")
            # On continue vers le private_reply, c'est l'essentiel

        # 4. Private reply (ouvre le DM Messenger)
        try:
            await self.send_private_reply(comment_id, rag_response)
        except Exception as e:
            logger.error(f"[Comment] Erreur private_reply: {e}")
            return

        self._record_reply(post_id, user_id)

        # 5. Log
        try:
            from app.db import crud
            await crud.log_message(
                db=db,
                tenant_id=tenant.id,
                sender_id=user_id,
                message_text=message,
                response_text=rag_response,
                confidence_level=classification["intent"],
                confidence_score=classification["confidence"],
                channel="comment",
            )
        except Exception as e:
            logger.error(f"[Comment] Erreur log: {e}")

    # ─── RAG ────────────────────────────────────────────────────

    async def _generate_rag_response_mt(
        self, query: str, intent: str, tenant, tenant_config, db
    ) -> str:
        from app.rag.pg_retriever import PgVectorRetriever
        from app.rag.generator import ResponseGenerator
        from app.rag.confidence import ConfidenceHandler

        # Pour les "mp", "inbox" etc. la query est vide de contenu produit
        # -> on envoie une intro generique pour ouvrir la conversation.
        if intent == "mp_request" or len(query.strip()) < 4:
            return (
                "Bonjour 👋\n\n"
                "Merci pour votre message ! Quel produit ou information vous interesse ? "
                "Nous sommes la pour repondre a toutes vos questions."
            )

        retriever = PgVectorRetriever(tenant_id=tenant.id, db=db)
        generator = ResponseGenerator(
            custom_system_prompt=(tenant_config.custom_system_prompt if tenant_config else None),
            conversation_mode=(getattr(tenant_config, "conversation_mode", "catalog") if tenant_config else "catalog"),
        )
        confidence = ConfidenceHandler()

        rag_response = await confidence.process_query_async(query, retriever, generator)
        text = rag_response.response or ""

        if len(text) > self.PRIVATE_REPLY_MAX_LEN:
            text = text[: self.PRIVATE_REPLY_MAX_LEN - 3] + "..."
        return text

    # ─── Meta API ────────────────────────────────────────────────

    async def reply_to_comment(self, comment_id: str, message: str, user_name: str = ""):
        """Reponse publique sous le commentaire."""
        if not self.access_token:
            return

        if user_name:
            message = f"@{user_name} {message}"
        message = message[: self.PUBLIC_REPLY_MAX_LEN]

        url = f"{self.GRAPH_API_URL}/{comment_id}/comments"
        params = {"access_token": self.access_token}
        payload = {"message": message}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=params, data=payload)
            if response.status_code != 200:
                logger.error(
                    f"[Comment] Public reply erreur {response.status_code}: {response.text}"
                )
            response.raise_for_status()
            logger.info(f"[Comment] Reponse publique envoyee sur {comment_id}")

    async def send_private_reply(self, comment_id: str, message: str):
        """
        Envoie un message Messenger prive a l'auteur du commentaire.
        Endpoint moderne : POST /me/messages avec recipient.comment_id
        (l'ancien /{comment_id}/private_replies est deprecated et echoue
        avec code=100 subcode=33 sur certains comments).
        Limites :
          - 7 jours apres la date du commentaire
          - 1 seul private_reply par commentaire
          - max ~2000 chars
        """
        if not self.access_token:
            return

        message = (message or "").strip()[: self.PRIVATE_REPLY_MAX_LEN]
        if not message:
            return

        url = f"{self.GRAPH_API_URL}/me/messages"
        params = {"access_token": self.access_token}
        payload = {
            "recipient": {"comment_id": comment_id},
            "message": {"text": message},
            "messaging_type": "RESPONSE",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=params, json=payload)
            if response.status_code != 200:
                logger.error(
                    f"[Comment] private_reply erreur {response.status_code}: {response.text}"
                )
                response.raise_for_status()
            logger.info(f"[Comment] private_reply envoye pour {comment_id}")
