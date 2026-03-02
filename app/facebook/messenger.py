"""
Client Messenger
Gestion des messages Facebook Messenger
"""

import httpx
from loguru import logger
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict

from app.config import settings


class MessengerClient:
    """
    Client pour l'API Facebook Messenger
    Gere l'envoi et la reception des messages
    """

    GRAPH_API_URL = "https://graph.facebook.com/v25.0"

    def __init__(self):
        """Initialise le client Messenger"""
        self.access_token = settings.facebook_page_access_token
        self._rag_services = None

        # Tracking des messages pour respecter la fenetre de 24h
        self._last_user_message: Dict[str, datetime] = defaultdict(lambda: datetime.min)

        logger.info("Client Messenger initialise")

    def set_rag_services(self, services: dict):
        """Configure les services RAG"""
        self._rag_services = services

    def _get_rag_services(self):
        """Recupere les services RAG depuis main"""
        if self._rag_services is None:
            from app.main import get_rag_services
            self._rag_services = get_rag_services()
        return self._rag_services

    def _is_within_24h_window(self, user_id: str) -> bool:
        """
        Verifie si on est dans la fenetre de 24h pour repondre

        Args:
            user_id: ID de l'utilisateur

        Returns:
            True si on peut repondre
        """
        last_message = self._last_user_message.get(user_id, datetime.min)
        return datetime.now() - last_message < timedelta(hours=24)

    async def handle_message(self, sender_id: str, message_text: str):
        """
        Traite un message entrant et genere une reponse

        Args:
            sender_id: ID de l'expediteur
            message_text: Contenu du message
        """
        # Mettre a jour le timestamp du dernier message
        self._last_user_message[sender_id] = datetime.now()

        try:
            # Envoyer l'indicateur de frappe
            await self.send_typing_indicator(sender_id, True)

            # Generer la reponse avec RAG
            response = await self._generate_rag_response(message_text)

            # Envoyer la reponse
            await self.send_message(sender_id, response)

        except Exception as e:
            logger.error(f"Erreur traitement message: {e}")
            await self.send_message(
                sender_id,
                "Desolee, je rencontre un probleme technique. "
                f"Veuillez contacter {settings.support_email} pour assistance."
            )

        finally:
            await self.send_typing_indicator(sender_id, False)

    async def _generate_rag_response(self, query: str) -> str:
        """
        Genere une reponse en utilisant le systeme RAG

        Args:
            query: Question de l'utilisateur

        Returns:
            Reponse generee
        """
        services = self._get_rag_services()

        if not services or not services.get("retriever"):
            logger.warning("Services RAG non disponibles")
            return (
                "Je suis en cours de configuration. "
                f"Pour toute question, contactez {settings.support_email}."
            )

        retriever = services["retriever"]
        generator = services["generator"]
        confidence = services["confidence"]

        # Utiliser le gestionnaire de confiance
        rag_response = confidence.process_query(query, retriever, generator)

        logger.info(
            f"Reponse RAG generee - Confiance: {rag_response.confidence_level.value} "
            f"({rag_response.confidence_score:.2f})"
        )

        return rag_response.response

    async def handle_postback(self, sender_id: str, payload: str):
        """
        Traite un postback (clic sur bouton)

        Args:
            sender_id: ID de l'utilisateur
            payload: Payload du postback
        """
        # Mettre a jour le timestamp
        self._last_user_message[sender_id] = datetime.now()

        if payload == "GET_STARTED":
            await self.send_welcome_message(sender_id)
        elif payload == "CONTACT_SUPPORT":
            await self.send_message(
                sender_id,
                f"Pour contacter notre support:\n"
                f"Email: {settings.support_email}\n"
                f"Telephone: {settings.support_phone}"
            )
        else:
            # Traiter comme une question
            await self.handle_message(sender_id, payload)

    async def send_welcome_message(self, sender_id: str):
        """Envoie le message de bienvenue"""
        welcome_text = (
            "Bonjour ! Je suis l'assistant virtuel de cette page.\n\n"
            "Je peux repondre a vos questions sur nos produits et services. "
            "N'hesitez pas a me poser vos questions !\n\n"
            "Si vous preferez parler a un conseiller, dites-le moi."
        )
        await self.send_message(sender_id, welcome_text)

    async def send_message(self, recipient_id: str, text: str):
        """
        Envoie un message texte

        Args:
            recipient_id: ID du destinataire
            text: Texte du message
        """
        if not self.access_token:
            logger.warning("Token d'acces non configure, message non envoye")
            return

        url = f"{self.GRAPH_API_URL}/me/messages"
        params = {"access_token": self.access_token}

        # Diviser les messages longs (limite Messenger: 2000 caracteres)
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
        """
        Envoie un message avec des boutons

        Args:
            recipient_id: ID du destinataire
            text: Texte du message
            buttons: Liste de boutons [{"title": "...", "payload": "..."}]
        """
        if not self.access_token:
            logger.warning("Token d'acces non configure")
            return

        url = f"{self.GRAPH_API_URL}/me/messages"
        params = {"access_token": self.access_token}

        # Formater les boutons pour l'API
        formatted_buttons = []
        for btn in buttons[:3]:  # Max 3 boutons
            formatted_buttons.append({
                "type": "postback",
                "title": btn["title"][:20],  # Max 20 caracteres
                "payload": btn["payload"]
            })

        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": text[:640],  # Max 640 caracteres
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
                logger.debug(f"Message avec boutons envoye a {recipient_id}")
            except httpx.HTTPError as e:
                logger.error(f"Erreur envoi message avec boutons: {e}")

    async def send_typing_indicator(self, recipient_id: str, is_typing: bool):
        """
        Envoie l'indicateur de frappe

        Args:
            recipient_id: ID du destinataire
            is_typing: True pour activer, False pour desactiver
        """
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
                pass  # Ignorer les erreurs de typing indicator

    def _split_long_message(self, text: str, max_length: int = 2000) -> List[str]:
        """
        Divise un message long en plusieurs parties

        Args:
            text: Texte a diviser
            max_length: Longueur maximale par message

        Returns:
            Liste de messages
        """
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
