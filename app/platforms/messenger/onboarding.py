"""
Onboarding conversationnel — guide le nouveau tenant via Messenger
Flow: welcome → bot_type → welcome_message → catalog_link → complete
"""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import crud


class OnboardingFlow:
    """Guide un nouveau tenant etape par etape via Messenger"""

    def __init__(self, messenger_client, tenant, tenant_config, db: AsyncSession):
        self.client = messenger_client
        self.tenant = tenant
        self.config = tenant_config
        self.db = db

    async def start(self):
        sender_id = self.tenant.page_id
        await self._handle_step("welcome", None, None)

    async def handle_message(self, sender_id: str, message_text: str):
        step = self.config.onboarding_step if self.config else "welcome"
        await self._handle_step(step, sender_id, message_text)

    async def _handle_step(self, step: str, sender_id: str, message_text: str):
        if step == "welcome":
            await self._step_welcome(sender_id)
        elif step == "bot_type":
            await self._step_bot_type(sender_id, message_text)
        elif step == "welcome_message":
            await self._step_welcome_message(sender_id, message_text)
        elif step == "catalog_prompt":
            await self._step_catalog_prompt(sender_id, message_text)
        elif step == "complete":
            pass

    async def _step_welcome(self, sender_id: str):
        await self.client.send_message(
            sender_id,
            f"Bienvenue sur {self.tenant.page_name} ! Je suis votre assistant IA.\n\n"
            "Pour commencer, quel type de bot souhaitez-vous ?\n\n"
            "1. E-commerce (vente de produits)\n"
            "2. Service client (FAQ, support)\n"
            "3. Restaurant (menu, commandes)\n"
            "4. Autre\n\n"
            "Repondez avec le numero ou le type."
        )
        await self._update_step("bot_type")

    async def _step_bot_type(self, sender_id: str, message_text: str):
        text = message_text.strip().lower()

        bot_type_map = {
            "1": "ecommerce", "ecommerce": "ecommerce", "e-commerce": "ecommerce",
            "2": "support", "service": "support", "faq": "support", "support": "support",
            "3": "restaurant", "resto": "restaurant", "restaurant": "restaurant",
            "4": "autre", "autre": "autre",
        }
        bot_type = bot_type_map.get(text, "ecommerce")

        await crud.update_tenant_config(self.db, self.tenant.id, bot_type=bot_type)

        await self.client.send_message(
            sender_id,
            f"Parfait ! Type de bot: {bot_type}\n\n"
            "Quel message d'accueil souhaitez-vous que le bot envoie ?\n\n"
            "Exemple: \"Bonjour ! Bienvenue chez [votre boutique]. Comment puis-je vous aider ?\"\n\n"
            "Ecrivez votre message ci-dessous :"
        )
        await self._update_step("welcome_message")

    async def _step_welcome_message(self, sender_id: str, message_text: str):
        await crud.update_tenant_config(
            self.db, self.tenant.id, welcome_message=message_text
        )

        dashboard_url = "https://facebook-dashboard-nine.vercel.app"

        await self.client.send_message(
            sender_id,
            f"Message d'accueil enregistre !\n\n"
            "Derniere etape : uploadez votre catalogue de produits (fichier Excel) "
            "pour que le bot puisse repondre aux questions sur vos produits.\n\n"
            f"Rendez-vous sur le dashboard :\n{dashboard_url}\n\n"
            "Ou envoyez 'OK' pour commencer a utiliser le bot sans catalogue."
        )
        await self._update_step("catalog_prompt")

    async def _step_catalog_prompt(self, sender_id: str, message_text: str):
        await crud.update_tenant_config(self.db, self.tenant.id, onboarding_step="complete")

        await self.client.send_message(
            sender_id,
            "Configuration terminee ! Votre bot est maintenant actif.\n\n"
            "Vos clients peuvent desormais envoyer des messages a votre page "
            "et le bot repondra automatiquement.\n\n"
            "Vous pouvez modifier la configuration a tout moment depuis le dashboard."
        )
        logger.info(f"Onboarding termine pour {self.tenant.page_name}")

    async def _update_step(self, step: str):
        await crud.update_tenant_config(self.db, self.tenant.id, onboarding_step=step)
