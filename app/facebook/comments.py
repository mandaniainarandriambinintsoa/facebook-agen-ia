"""
Gestionnaire de commentaires Facebook
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
    """
    Gestionnaire des commentaires Facebook
    Repond aux commentaires avec le systeme RAG
    """

    GRAPH_API_URL = "https://graph.facebook.com/v25.0"

    # Rate limiting pour eviter le spam
    MIN_DELAY_BETWEEN_REPLIES = 5  # secondes
    MAX_REPLIES_PER_POST = 50  # par heure
    MAX_REPLIES_PER_USER = 3  # par heure

    def __init__(self):
        """Initialise le gestionnaire de commentaires"""
        self.access_token = settings.facebook_page_access_token
        self._rag_services = None

        # Rate limiting tracking
        self._post_reply_count: Dict[str, list] = defaultdict(list)
        self._user_reply_count: Dict[str, list] = defaultdict(list)
        self._last_reply_time: datetime = datetime.min

        logger.info("CommentsHandler initialise")

    def set_rag_services(self, services: dict):
        """Configure les services RAG"""
        self._rag_services = services

    def _get_rag_services(self):
        """Recupere les services RAG"""
        if self._rag_services is None:
            from app.main import get_rag_services
            self._rag_services = get_rag_services()
        return self._rag_services

    def _can_reply(self, post_id: str, user_id: str) -> bool:
        """
        Verifie si on peut repondre (rate limiting)

        Args:
            post_id: ID du post
            user_id: ID de l'utilisateur

        Returns:
            True si on peut repondre
        """
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)

        # Nettoyer les anciennes entrees
        self._post_reply_count[post_id] = [
            t for t in self._post_reply_count[post_id] if t > one_hour_ago
        ]
        self._user_reply_count[user_id] = [
            t for t in self._user_reply_count[user_id] if t > one_hour_ago
        ]

        # Verifier les limites
        if len(self._post_reply_count[post_id]) >= self.MAX_REPLIES_PER_POST:
            logger.warning(f"Limite de reponses atteinte pour le post {post_id}")
            return False

        if len(self._user_reply_count[user_id]) >= self.MAX_REPLIES_PER_USER:
            logger.warning(f"Limite de reponses atteinte pour l'utilisateur {user_id}")
            return False

        # Verifier le delai minimum
        if (now - self._last_reply_time).total_seconds() < self.MIN_DELAY_BETWEEN_REPLIES:
            logger.debug("Delai minimum entre reponses non respecte")
            return False

        return True

    def _record_reply(self, post_id: str, user_id: str):
        """Enregistre une reponse pour le rate limiting"""
        now = datetime.now()
        self._post_reply_count[post_id].append(now)
        self._user_reply_count[user_id].append(now)
        self._last_reply_time = now

    async def handle_comment(
        self,
        comment_id: str,
        post_id: str,
        message: str,
        from_user: Dict[str, Any]
    ):
        """
        Traite un nouveau commentaire

        Args:
            comment_id: ID du commentaire
            post_id: ID du post
            message: Texte du commentaire
            from_user: Informations sur l'auteur
        """
        user_id = from_user.get("id", "unknown")
        user_name = from_user.get("name", "")

        logger.info(f"Traitement commentaire de {user_name}: {message[:50]}...")

        # Verifier le rate limiting
        if not self._can_reply(post_id, user_id):
            logger.info("Reponse ignoree (rate limiting)")
            return

        # Verifier si c'est une question qui merite une reponse
        if not self._should_reply(message):
            logger.debug("Commentaire ignore (pas une question)")
            return

        try:
            # Generer la reponse avec RAG
            response = await self._generate_rag_response(message)

            # Ajouter un delai naturel
            await asyncio.sleep(2)

            # Repondre au commentaire
            await self.reply_to_comment(comment_id, response, user_name)

            # Enregistrer la reponse
            self._record_reply(post_id, user_id)

        except Exception as e:
            logger.error(f"Erreur traitement commentaire: {e}")

    def _should_reply(self, message: str) -> bool:
        """
        Determine si le commentaire merite une reponse

        Args:
            message: Texte du commentaire

        Returns:
            True si on devrait repondre
        """
        message_lower = message.lower().strip()

        # Ignorer les messages trop courts
        if len(message) < 5:
            return False

        # Ignorer les emojis seuls
        if not any(c.isalpha() for c in message):
            return False

        # Indicateurs de question
        question_indicators = ["?", "comment", "pourquoi", "quand", "ou", "qui",
                              "combien", "quel", "quelle", "est-ce", "y a-t-il",
                              "pouvez", "puis-je", "avez-vous", "c'est quoi"]

        # Verifier si c'est une question
        is_question = any(ind in message_lower for ind in question_indicators)

        # Ou si c'est une demande d'information
        info_requests = ["info", "renseignement", "savoir", "besoin", "cherche",
                        "prix", "tarif", "horaire", "adresse", "contact"]
        is_info_request = any(req in message_lower for req in info_requests)

        return is_question or is_info_request

    async def _generate_rag_response(self, query: str) -> str:
        """
        Genere une reponse avec le systeme RAG

        Args:
            query: Question de l'utilisateur

        Returns:
            Reponse generee
        """
        services = self._get_rag_services()

        if not services or not services.get("retriever"):
            return (
                "Merci pour votre question ! "
                "Pour plus d'informations, envoyez-nous un message prive "
                "ou contactez-nous par email."
            )

        retriever = services["retriever"]
        generator = services["generator"]
        confidence = services["confidence"]

        rag_response = confidence.process_query(query, retriever, generator)

        # Pour les commentaires, raccourcir la reponse
        response = rag_response.response
        if len(response) > 500:
            response = response[:497] + "..."
            response += "\n\nPour plus de details, envoyez-nous un message prive !"

        return response

    async def reply_to_comment(
        self,
        comment_id: str,
        message: str,
        user_name: str = ""
    ):
        """
        Repond a un commentaire

        Args:
            comment_id: ID du commentaire
            message: Reponse a envoyer
            user_name: Nom de l'utilisateur (pour personnalisation)
        """
        if not self.access_token:
            logger.warning("Token d'acces non configure")
            return

        # Personnaliser la reponse
        if user_name:
            message = f"@{user_name} {message}"

        url = f"{self.GRAPH_API_URL}/{comment_id}/comments"
        params = {"access_token": self.access_token}

        payload = {
            "message": message[:8000]  # Limite Facebook pour les commentaires
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, params=params, data=payload)
                response.raise_for_status()
                logger.info(f"Reponse envoyee au commentaire {comment_id}")
            except httpx.HTTPError as e:
                logger.error(f"Erreur envoi reponse commentaire: {e}")
                raise

    async def like_comment(self, comment_id: str):
        """
        Like un commentaire

        Args:
            comment_id: ID du commentaire
        """
        if not self.access_token:
            return

        url = f"{self.GRAPH_API_URL}/{comment_id}/likes"
        params = {"access_token": self.access_token}

        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, params=params)
                logger.debug(f"Commentaire {comment_id} like")
            except httpx.HTTPError:
                pass  # Ignorer les erreurs de like

    async def hide_comment(self, comment_id: str):
        """
        Masque un commentaire (pour moderation)

        Args:
            comment_id: ID du commentaire
        """
        if not self.access_token:
            return

        url = f"{self.GRAPH_API_URL}/{comment_id}"
        params = {"access_token": self.access_token}
        payload = {"is_hidden": True}

        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, params=params, data=payload)
                logger.info(f"Commentaire {comment_id} masque")
            except httpx.HTTPError as e:
                logger.error(f"Erreur masquage commentaire: {e}")
