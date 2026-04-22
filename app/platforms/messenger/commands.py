"""
Routeur de commandes et gestionnaire d'actions interactives
Gere les commandes texte (/menu, /produits, etc.), postbacks et quick replies
"""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import crud


# ─── Quick Replies contextuels ───────────────────────────────

def get_contextual_quick_replies(confidence_level: str) -> list[dict]:
    """Retourne des quick replies adaptes au niveau de confiance RAG"""
    if confidence_level == "high":
        return [
            {"title": "Voir produits", "payload": "CMD_PRODUCTS"},
            {"title": "Commander", "payload": "CMD_ORDER"},
            {"title": "Autre question", "payload": "CMD_MENU"},
        ]
    elif confidence_level in ("medium", "low"):
        return [
            {"title": "Voir produits", "payload": "CMD_PRODUCTS"},
            {"title": "Parler a un agent", "payload": "CMD_AGENT"},
            {"title": "Aide", "payload": "CMD_HELP"},
        ]
    else:
        return [
            {"title": "Parler a un agent", "payload": "CMD_AGENT"},
            {"title": "Menu", "payload": "CMD_MENU"},
        ]


class CommandRouter:
    """
    Routeur de commandes pour le chatbot.
    Gere les postbacks, quick replies et commandes texte.
    Fonctionne avec n'importe quel PlatformClient.
    """

    # Mapping commandes texte → payload
    TEXT_COMMANDS = {
        "/menu": "CMD_MENU",
        "menu": "CMD_MENU",
        "/produits": "CMD_PRODUCTS",
        "produits": "CMD_PRODUCTS",
        "voir produits": "CMD_PRODUCTS",
        "/aide": "CMD_HELP",
        "aide": "CMD_HELP",
        "/agent": "CMD_AGENT",
        "agent": "CMD_AGENT",
        "parler a un agent": "CMD_AGENT",
        "commander": "CMD_ORDER",
        "/commander": "CMD_ORDER",
    }

    def __init__(self, client, tenant, tenant_config, db: AsyncSession):
        self.client = client
        self.tenant = tenant
        self.config = tenant_config
        self.db = db

    async def handle(self, sender_id: str, input_text: str) -> bool:
        """
        Tente de traiter l'input comme une commande.
        Retourne True si une commande a ete traitee, False sinon (→ RAG).
        En mode conversation_mode=classic, toutes les commandes sont bypass pour
        forcer le texte conversationnel via le pipeline RAG.
        """
        if not input_text:
            return False

        if self.config and getattr(self.config, "conversation_mode", "catalog") == "classic":
            return False

        payload = input_text.strip()
        text_lower = payload.lower()
        if text_lower in self.TEXT_COMMANDS:
            payload = self.TEXT_COMMANDS[text_lower]

        if payload == "GET_STARTED":
            await self._handle_get_started(sender_id)
            return True
        elif payload == "CMD_MENU":
            await self._handle_menu(sender_id)
            return True
        elif payload == "CMD_PRODUCTS":
            await self._handle_products(sender_id)
            return True
        elif payload == "CMD_AGENT":
            await self._handle_agent(sender_id)
            return True
        elif payload == "CMD_HELP":
            await self._handle_help(sender_id)
            return True
        elif payload == "CMD_ORDER":
            await self._handle_order(sender_id)
            return True
        elif payload.startswith("ORDER_"):
            product_id = payload.replace("ORDER_", "")
            await self._handle_order_product(sender_id, product_id)
            return True
        elif payload.startswith("DETAIL_"):
            product_id = payload.replace("DETAIL_", "")
            await self._handle_detail_product(sender_id, product_id)
            return True
        elif payload.startswith("CATEGORY_"):
            category = payload.replace("CATEGORY_", "")
            await self._handle_category(sender_id, category)
            return True

        return False

    # ─── Handlers de commandes ────────────────────────────────

    async def _handle_get_started(self, sender_id: str):
        welcome = "Bienvenue ! Comment puis-je vous aider ?"
        if self.config and self.config.welcome_message:
            welcome = self.config.welcome_message

        await self.client.send_quick_replies(
            sender_id,
            welcome,
            quick_replies=[
                {"title": "Voir produits", "payload": "CMD_PRODUCTS"},
                {"title": "Commander", "payload": "CMD_ORDER"},
                {"title": "Aide", "payload": "CMD_HELP"},
                {"title": "Parler a un agent", "payload": "CMD_AGENT"},
            ],
        )

    async def _handle_menu(self, sender_id: str):
        await self.client.send_quick_replies(
            sender_id,
            "Menu principal — Que souhaitez-vous faire ?",
            quick_replies=[
                {"title": "Voir produits", "payload": "CMD_PRODUCTS"},
                {"title": "Commander", "payload": "CMD_ORDER"},
                {"title": "Aide", "payload": "CMD_HELP"},
                {"title": "Parler a un agent", "payload": "CMD_AGENT"},
            ],
        )

    async def _handle_products(self, sender_id: str):
        try:
            products = await crud.search_products(
                self.db, self.tenant.id, limit=10
            )

            if not products:
                await self.client.send_quick_replies(
                    sender_id,
                    "Aucun produit disponible pour le moment.",
                    quick_replies=[
                        {"title": "Menu", "payload": "CMD_MENU"},
                        {"title": "Parler a un agent", "payload": "CMD_AGENT"},
                    ],
                )
                return

            elements = []
            for product in products:
                subtitle_parts = []
                if product.price:
                    subtitle_parts.append(product.price)
                if product.stock_status:
                    subtitle_parts.append(product.stock_status.capitalize())
                subtitle = " — ".join(subtitle_parts) if subtitle_parts else ""

                element = {
                    "title": product.name,
                    "subtitle": subtitle,
                    "buttons": [
                        {
                            "type": "postback",
                            "title": "Commander",
                            "payload": f"ORDER_{product.id}",
                        },
                        {
                            "type": "postback",
                            "title": "Details",
                            "payload": f"DETAIL_{product.id}",
                        },
                    ],
                }

                if product.image_url:
                    element["image_url"] = product.image_url

                elements.append(element)

            await self.client.send_generic_template(sender_id, elements)

            categories = await crud.get_product_categories(self.db, self.tenant.id)
            qr = [{"title": "Menu", "payload": "CMD_MENU"}]
            for cat in categories[:4]:
                qr.append({"title": cat[:20], "payload": f"CATEGORY_{cat}"})

            if len(qr) > 1:
                await self.client.send_quick_replies(
                    sender_id,
                    "Filtrer par categorie :",
                    quick_replies=qr,
                )

        except Exception as e:
            logger.error(f"Erreur affichage produits: {e}")
            await self.client.send_message(
                sender_id,
                "Desolee, je n'arrive pas a afficher les produits. Reessayez."
            )

    async def _handle_agent(self, sender_id: str):
        contact_parts = []
        if self.config and self.config.phone_numbers:
            phones = self.config.phone_numbers
            if isinstance(phones, list) and phones:
                contact_parts.append(f"Telephone : {phones[0]}")

        from app.config import settings
        if settings.support_email:
            contact_parts.append(f"Email : {settings.support_email}")

        contact_info = "\n".join(contact_parts) if contact_parts else ""

        message = (
            "Je vous mets en relation avec un agent humain.\n\n"
            "Un membre de notre equipe vous repondra dans les plus brefs delais."
        )
        if contact_info:
            message += f"\n\nVous pouvez aussi nous contacter directement :\n{contact_info}"

        await self.client.send_quick_replies(
            sender_id,
            message,
            quick_replies=[
                {"title": "Menu", "payload": "CMD_MENU"},
                {"title": "Voir produits", "payload": "CMD_PRODUCTS"},
            ],
        )

    async def _handle_help(self, sender_id: str):
        help_text = (
            "Voici ce que je peux faire pour vous :\n\n"
            "• \"produits\" — Voir notre catalogue\n"
            "• \"menu\" — Retour au menu principal\n"
            "• \"commander\" — Comment passer commande\n"
            "• \"agent\" — Parler a un humain\n"
            "• \"aide\" — Afficher cette aide\n\n"
            "Vous pouvez aussi poser une question libre et je chercherai la reponse !"
        )
        await self.client.send_quick_replies(
            sender_id,
            help_text,
            quick_replies=[
                {"title": "Voir produits", "payload": "CMD_PRODUCTS"},
                {"title": "Menu", "payload": "CMD_MENU"},
                {"title": "Parler a un agent", "payload": "CMD_AGENT"},
            ],
        )

    async def _handle_order(self, sender_id: str):
        await self.client.send_quick_replies(
            sender_id,
            "Pour commander :\n\n"
            "1. Parcourez nos produits\n"
            "2. Cliquez sur \"Commander\" sur le produit souhaite\n"
            "3. Indiquez la taille/couleur/quantite\n\n"
            "Ou decrivez simplement ce que vous souhaitez commander !",
            quick_replies=[
                {"title": "Voir produits", "payload": "CMD_PRODUCTS"},
                {"title": "Menu", "payload": "CMD_MENU"},
                {"title": "Parler a un agent", "payload": "CMD_AGENT"},
            ],
        )

    async def _handle_order_product(self, sender_id: str, product_id: str):
        try:
            import uuid
            product = await crud.get_product_by_id(self.db, uuid.UUID(product_id))

            if not product:
                await self.client.send_message(sender_id, "Produit introuvable.")
                return

            details = [f"Vous souhaitez commander : {product.name}"]
            if product.price:
                details.append(f"Prix : {product.price}")
            if product.sizes:
                details.append(f"Tailles disponibles : {product.sizes}")
            if product.colors:
                details.append(f"Couleurs disponibles : {product.colors}")

            details.append(
                "\nPour finaliser votre commande, indiquez :\n"
                "• Taille souhaitee\n"
                "• Couleur souhaitee\n"
                "• Quantite"
            )

            await self.client.send_quick_replies(
                sender_id,
                "\n".join(details),
                quick_replies=[
                    {"title": "Parler a un agent", "payload": "CMD_AGENT"},
                    {"title": "Voir produits", "payload": "CMD_PRODUCTS"},
                    {"title": "Menu", "payload": "CMD_MENU"},
                ],
            )
        except Exception as e:
            logger.error(f"Erreur commande produit {product_id}: {e}")
            await self.client.send_message(sender_id, "Erreur lors du chargement du produit.")

    async def _handle_detail_product(self, sender_id: str, product_id: str):
        try:
            import uuid
            product = await crud.get_product_by_id(self.db, uuid.UUID(product_id))

            if not product:
                await self.client.send_message(sender_id, "Produit introuvable.")
                return

            details = [f"{product.name}"]
            if product.description:
                details.append(f"\n{product.description}")
            if product.price:
                details.append(f"\nPrix : {product.price}")
            if product.category:
                details.append(f"Categorie : {product.category}")
            if product.sizes:
                details.append(f"Tailles : {product.sizes}")
            if product.colors:
                details.append(f"Couleurs : {product.colors}")
            if product.stock_status:
                details.append(f"Disponibilite : {product.stock_status}")

            await self.client.send_quick_replies(
                sender_id,
                "\n".join(details),
                quick_replies=[
                    {"title": "Commander", "payload": f"ORDER_{product.id}"},
                    {"title": "Voir produits", "payload": "CMD_PRODUCTS"},
                    {"title": "Menu", "payload": "CMD_MENU"},
                ],
            )
        except Exception as e:
            logger.error(f"Erreur detail produit {product_id}: {e}")
            await self.client.send_message(sender_id, "Erreur lors du chargement du produit.")

    async def _handle_category(self, sender_id: str, category: str):
        try:
            products = await crud.search_products(
                self.db, self.tenant.id, category=category, limit=10
            )

            if not products:
                await self.client.send_quick_replies(
                    sender_id,
                    f"Aucun produit dans la categorie \"{category}\".",
                    quick_replies=[
                        {"title": "Voir produits", "payload": "CMD_PRODUCTS"},
                        {"title": "Menu", "payload": "CMD_MENU"},
                    ],
                )
                return

            elements = []
            for product in products:
                subtitle_parts = []
                if product.price:
                    subtitle_parts.append(product.price)
                if product.stock_status:
                    subtitle_parts.append(product.stock_status.capitalize())
                subtitle = " — ".join(subtitle_parts) if subtitle_parts else ""

                element = {
                    "title": product.name,
                    "subtitle": subtitle,
                    "buttons": [
                        {
                            "type": "postback",
                            "title": "Commander",
                            "payload": f"ORDER_{product.id}",
                        },
                        {
                            "type": "postback",
                            "title": "Details",
                            "payload": f"DETAIL_{product.id}",
                        },
                    ],
                }

                image_url = (product.metadata_ or {}).get("image_url")
                if image_url:
                    element["image_url"] = image_url

                elements.append(element)

            await self.client.send_generic_template(sender_id, elements)

        except Exception as e:
            logger.error(f"Erreur categorie {category}: {e}")
            await self.client.send_message(
                sender_id,
                "Erreur lors du chargement de la categorie."
            )
