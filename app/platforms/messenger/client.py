"""
Client Messenger — Implementation Facebook Messenger de PlatformClient
"""

import httpx
from loguru import logger
from typing import Dict, List
from datetime import datetime
from collections import defaultdict

from app.config import settings
from app.platforms.base import PlatformClient


class MessengerClient(PlatformClient):
    """Client pour l'API Facebook Messenger"""

    def __init__(self, access_token: str = None):
        super().__init__(access_token=access_token or settings.facebook_page_access_token)
        self._last_user_message: Dict[str, datetime] = defaultdict(lambda: datetime.min)

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
        """Envoie un message avec des boutons postback"""
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

    async def send_quick_replies(
        self,
        recipient_id: str,
        text: str,
        quick_replies: list[dict],
    ):
        """Envoie un message avec des quick replies (max 13, titre max 20 chars)"""
        if not self.access_token:
            return

        url = f"{self.GRAPH_API_URL}/me/messages"
        params = {"access_token": self.access_token}

        formatted_qr = []
        for qr in quick_replies[:13]:
            formatted_qr.append({
                "content_type": "text",
                "title": qr["title"][:20],
                "payload": qr["payload"],
            })

        messages = self._split_long_message(text, max_length=2000)

        async with httpx.AsyncClient() as client:
            for msg in messages[:-1]:
                payload = {
                    "recipient": {"id": recipient_id},
                    "message": {"text": msg},
                    "messaging_type": "RESPONSE",
                }
                try:
                    response = await client.post(url, params=params, json=payload)
                    response.raise_for_status()
                except httpx.HTTPError as e:
                    logger.error(f"Erreur envoi message: {e}")

            payload = {
                "recipient": {"id": recipient_id},
                "message": {
                    "text": messages[-1],
                    "quick_replies": formatted_qr,
                },
                "messaging_type": "RESPONSE",
            }
            try:
                response = await client.post(url, params=params, json=payload)
                if response.status_code != 200:
                    logger.error(f"Facebook API erreur {response.status_code}: {response.text}")
                response.raise_for_status()
            except httpx.HTTPError as e:
                logger.error(f"Erreur envoi quick replies: {e}")

    async def send_generic_template(
        self,
        recipient_id: str,
        elements: list[dict],
    ):
        """Envoie un carousel de cartes (generic template, max 10 elements)"""
        if not self.access_token:
            return

        url = f"{self.GRAPH_API_URL}/me/messages"
        params = {"access_token": self.access_token}

        formatted_elements = []
        for el in elements[:10]:
            element = {
                "title": el["title"][:80],
            }
            if el.get("subtitle"):
                element["subtitle"] = el["subtitle"][:80]
            if el.get("image_url"):
                element["image_url"] = el["image_url"]
            if el.get("buttons"):
                element["buttons"] = el["buttons"][:3]
            formatted_elements.append(element)

        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": formatted_elements,
                    },
                }
            },
            "messaging_type": "RESPONSE",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, params=params, json=payload)
                if response.status_code != 200:
                    logger.error(f"Facebook API erreur {response.status_code}: {response.text}")
                response.raise_for_status()
            except httpx.HTTPError as e:
                logger.error(f"Erreur envoi generic template: {e}")

    async def setup_persistent_menu(self):
        """Configure le menu persistant et le bouton Get Started"""
        if not self.access_token:
            return

        url = f"{self.GRAPH_API_URL}/me/messenger_profile"
        params = {"access_token": self.access_token}

        payload = {
            "persistent_menu": [
                {
                    "locale": "default",
                    "composer_input_disabled": False,
                    "call_to_actions": [
                        {"type": "postback", "title": "Menu principal", "payload": "CMD_MENU"},
                        {"type": "postback", "title": "Nos produits", "payload": "CMD_PRODUCTS"},
                        {"type": "postback", "title": "Parler a un agent", "payload": "CMD_AGENT"},
                    ],
                }
            ],
            "get_started": {"payload": "GET_STARTED"},
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, params=params, json=payload)
                if response.status_code == 200:
                    logger.info("Menu persistant configure avec succes")
                else:
                    logger.error(f"Erreur config menu persistant: {response.status_code} {response.text}")
            except httpx.HTTPError as e:
                logger.error(f"Erreur setup menu persistant: {e}")

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
