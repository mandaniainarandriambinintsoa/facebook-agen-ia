"""
Client WhatsApp Business — Implementation WhatsApp de PlatformClient
Utilise la Cloud API Meta avec un format de payload different
"""

import httpx
from loguru import logger
from typing import List, Dict

from app.platforms.base import PlatformClient


class WhatsAppClient(PlatformClient):
    """Client pour l'API WhatsApp Business (Cloud API)"""

    def __init__(self, access_token: str, phone_number_id: str):
        super().__init__(access_token=access_token)
        self.phone_number_id = phone_number_id

    def _get_url(self) -> str:
        return f"{self.GRAPH_API_URL}/{self.phone_number_id}/messages"

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def send_message(self, recipient_phone: str, text: str):
        """Envoie un message texte via WhatsApp"""
        if not self.access_token:
            return

        messages = self._split_long_message(text, max_length=4096)

        async with httpx.AsyncClient() as client:
            for msg in messages:
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": recipient_phone,
                    "type": "text",
                    "text": {"body": msg}
                }
                try:
                    response = await client.post(
                        self._get_url(),
                        headers=self._get_headers(),
                        json=payload,
                    )
                    if response.status_code != 200:
                        logger.error(f"WhatsApp API erreur {response.status_code}: {response.text}")
                    response.raise_for_status()
                    logger.debug(f"[WhatsApp] Message envoye a {recipient_phone}")
                except httpx.HTTPError as e:
                    logger.error(f"[WhatsApp] Erreur envoi message: {e}")
                    raise

    async def send_quick_replies(self, recipient_phone: str, text: str, quick_replies: list[dict]):
        """WhatsApp supporte les boutons interactifs (max 3) sinon degrade en texte"""
        if len(quick_replies) <= 3:
            buttons = []
            for qr in quick_replies[:3]:
                buttons.append({
                    "type": "reply",
                    "reply": {
                        "id": qr["payload"],
                        "title": qr["title"][:20],
                    }
                })

            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_phone,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": text[:1024]},
                    "action": {"buttons": buttons}
                }
            }

            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        self._get_url(),
                        headers=self._get_headers(),
                        json=payload,
                    )
                    if response.status_code != 200:
                        logger.error(f"WhatsApp API erreur {response.status_code}: {response.text}")
                    response.raise_for_status()
                except httpx.HTTPError as e:
                    logger.error(f"[WhatsApp] Erreur envoi boutons: {e}")
        else:
            # Plus de 3 options → degrade en texte
            options = "\n".join(f"  • {qr['title']}" for qr in quick_replies)
            await self.send_message(recipient_phone, f"{text}\n\n{options}")

    async def send_generic_template(self, recipient_phone: str, elements: list[dict]):
        """WhatsApp n'a pas de carousel → utilise une list message (max 10 rows)"""
        rows = []
        for el in elements[:10]:
            row = {
                "id": el.get("buttons", [{}])[0].get("payload", f"DETAIL_{el['title']}") if el.get("buttons") else el["title"],
                "title": el["title"][:24],
            }
            if el.get("subtitle"):
                row["description"] = el["subtitle"][:72]
            rows.append(row)

        if rows:
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_phone,
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "body": {"text": "Voici nos produits :"},
                    "action": {
                        "button": "Voir produits",
                        "sections": [{
                            "title": "Catalogue",
                            "rows": rows,
                        }]
                    }
                }
            }

            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        self._get_url(),
                        headers=self._get_headers(),
                        json=payload,
                    )
                    if response.status_code != 200:
                        logger.error(f"WhatsApp API erreur {response.status_code}: {response.text}")
                    response.raise_for_status()
                except httpx.HTTPError as e:
                    logger.error(f"[WhatsApp] Erreur envoi list: {e}")
        else:
            await self.send_message(recipient_phone, "Aucun produit disponible.")

    async def send_message_with_buttons(self, recipient_phone: str, text: str, buttons: List[Dict[str, str]]):
        """WhatsApp boutons interactifs (max 3)"""
        qr = [{"title": btn["title"], "payload": btn["payload"]} for btn in buttons[:3]]
        await self.send_quick_replies(recipient_phone, text, qr)

    async def send_typing_indicator(self, recipient_phone: str, is_typing: bool):
        """WhatsApp n'a pas de typing indicator natif — no-op"""
        pass

    async def send_image(self, recipient_phone: str, image_url: str, caption: str = ""):
        """Envoie une image via WhatsApp Cloud API (type=image, link=url)"""
        if not self.access_token or not image_url:
            return

        image_payload = {"link": image_url}
        if caption:
            image_payload["caption"] = caption[:1024]

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_phone,
            "type": "image",
            "image": image_payload,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self._get_url(),
                    headers=self._get_headers(),
                    json=payload,
                )
                if response.status_code != 200:
                    logger.error(f"[WhatsApp] send_image erreur {response.status_code}: {response.text}")
            except httpx.HTTPError as e:
                logger.error(f"[WhatsApp] Erreur envoi image: {e}")

    async def mark_as_read(self, message_id: str):
        """Marque un message comme lu (ticks bleus)"""
        if not self.access_token or not message_id:
            return

        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self._get_url(),
                    headers=self._get_headers(),
                    json=payload,
                )
                if response.status_code != 200:
                    logger.debug(f"WhatsApp mark_as_read erreur: {response.text}")
            except httpx.HTTPError:
                pass
