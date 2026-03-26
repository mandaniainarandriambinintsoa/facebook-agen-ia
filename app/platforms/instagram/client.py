"""
Client Instagram DMs — Implementation Instagram de PlatformClient
Utilise la meme Graph API Meta mais sans quick replies ni carousels
"""

import httpx
from loguru import logger
from typing import List, Dict

from app.platforms.base import PlatformClient


class InstagramClient(PlatformClient):
    """Client pour l'API Instagram Messaging (Graph API)"""

    async def send_message(self, recipient_id: str, text: str):
        """Envoie un message texte via Instagram DM"""
        if not self.access_token:
            return

        url = f"{self.GRAPH_API_URL}/me/messages"
        params = {"access_token": self.access_token}
        messages = self._split_long_message(text, max_length=1000)

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
                        logger.error(f"Instagram API erreur {response.status_code}: {response.text}")
                    response.raise_for_status()
                    logger.debug(f"[Instagram] Message envoye a {recipient_id}")
                except httpx.HTTPError as e:
                    logger.error(f"[Instagram] Erreur envoi message: {e}")
                    raise

    async def send_quick_replies(self, recipient_id: str, text: str, quick_replies: list[dict]):
        """Instagram ne supporte pas les quick replies → degrade en texte avec options"""
        options = "\n".join(f"  • {qr['title']}" for qr in quick_replies)
        full_text = f"{text}\n\n{options}" if quick_replies else text
        await self.send_message(recipient_id, full_text)

    async def send_generic_template(self, recipient_id: str, elements: list[dict]):
        """Instagram ne supporte pas les carousels → degrade en liste texte"""
        lines = []
        for i, el in enumerate(elements, 1):
            line = f"{i}. {el['title']}"
            if el.get("subtitle"):
                line += f" — {el['subtitle']}"
            lines.append(line)

        text = "Nos produits :\n\n" + "\n".join(lines)
        if lines:
            text += "\n\nRepondez avec le numero du produit pour plus de details."

        await self.send_message(recipient_id, text)

    async def send_message_with_buttons(self, recipient_id: str, text: str, buttons: List[Dict[str, str]]):
        """Instagram ne supporte pas les boutons → degrade en texte"""
        options = "\n".join(f"  • {btn['title']}" for btn in buttons)
        await self.send_message(recipient_id, f"{text}\n\n{options}")

    async def send_typing_indicator(self, recipient_id: str, is_typing: bool):
        """Instagram supporte le typing indicator"""
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
