"""
Gestionnaire de commentaires Facebook — Multi-Tenant
Repond automatiquement aux commentaires sur les posts
"""

import httpx
from loguru import logger
from typing import Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

from app.config import settings


class CommentsHandler:
    """Gestionnaire des commentaires Facebook"""

    GRAPH_API_URL = "https://graph.facebook.com/v25.0"

    MIN_DELAY_BETWEEN_REPLIES = 5
    MAX_REPLIES_PER_POST = 50
    MAX_REPLIES_PER_USER = 3

    def __init__(self, access_token: str = None):
        self.access_token = access_token or settings.facebook_page_access_token
        self._post_reply_count: Dict[str, list] = defaultdict(list)
        self._user_reply_count: Dict[str, list] = defaultdict(list)
        self._last_reply_time: datetime = datetime.min

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

    def _should_reply(self, message: str) -> bool:
        message_lower = message.lower().strip()
        if len(message) < 5:
            return False
        if not any(c.isalpha() for c in message):
            return False

        question_indicators = ["?", "comment", "pourquoi", "quand", "ou", "qui",
                              "combien", "quel", "quelle", "est-ce", "y a-t-il",
                              "pouvez", "puis-je", "avez-vous", "c'est quoi"]
        is_question = any(ind in message_lower for ind in question_indicators)

        info_requests = ["info", "renseignement", "savoir", "besoin", "cherche",
                        "prix", "tarif", "horaire", "adresse", "contact"]
        is_info_request = any(req in message_lower for req in info_requests)

        return is_question or is_info_request

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
            return
        if not self._should_reply(message):
            return

        try:
            response = await self._generate_rag_response_mt(message, tenant, tenant_config, db)
            if len(response) > 500:
                response = response[:497] + "..."
                response += "\n\nPour plus de details, envoyez-nous un message prive !"

            await asyncio.sleep(2)
            await self.reply_to_comment(comment_id, response, user_name)
            self._record_reply(post_id, user_id)

            from app.db import crud
            try:
                await crud.log_message(
                    db=db,
                    tenant_id=tenant.id,
                    sender_id=user_id,
                    message_text=message,
                    response_text=response,
                    confidence_level="",
                    confidence_score=0.0,
                    channel="comment",
                )
            except Exception as e:
                logger.error(f"Erreur log commentaire: {e}")

        except Exception as e:
            logger.error(f"Erreur traitement commentaire MT: {e}")

    async def _generate_rag_response_mt(self, query: str, tenant, tenant_config, db) -> str:
        from app.rag.pg_retriever import PgVectorRetriever
        from app.rag.generator import ResponseGenerator
        from app.rag.confidence import ConfidenceHandler

        retriever = PgVectorRetriever(tenant_id=tenant.id, db=db)
        generator = ResponseGenerator(
            custom_system_prompt=(tenant_config.custom_system_prompt if tenant_config else None),
            conversation_mode=(getattr(tenant_config, "conversation_mode", "catalog") if tenant_config else "catalog"),
        )
        confidence = ConfidenceHandler()

        rag_response = await confidence.process_query_async(query, retriever, generator)
        return rag_response.response

    async def reply_to_comment(self, comment_id: str, message: str, user_name: str = ""):
        if not self.access_token:
            return

        if user_name:
            message = f"@{user_name} {message}"

        url = f"{self.GRAPH_API_URL}/{comment_id}/comments"
        params = {"access_token": self.access_token}
        payload = {"message": message[:8000]}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, params=params, data=payload)
                response.raise_for_status()
                logger.info(f"Reponse envoyee au commentaire {comment_id}")
            except httpx.HTTPError as e:
                logger.error(f"Erreur envoi reponse commentaire: {e}")
                raise
