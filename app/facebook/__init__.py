"""
Module d'integration Facebook
Gestion des webhooks, messages Messenger et commentaires
"""

from .webhooks import router as webhooks_router
from .messenger import MessengerClient
from .comments import CommentsHandler

__all__ = ["webhooks_router", "MessengerClient", "CommentsHandler"]
