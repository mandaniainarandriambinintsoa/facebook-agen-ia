"""
Module d'integration Facebook — Shim de retrocompatibilite
Le code reel est dans app.platforms.messenger.*
"""

from app.platforms.messenger.webhooks import router as webhooks_router
from app.platforms.messenger.client import MessengerClient
from app.platforms.messenger.comments import CommentsHandler

__all__ = ["webhooks_router", "MessengerClient", "CommentsHandler"]
