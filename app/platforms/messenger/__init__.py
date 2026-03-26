"""
Plateforme Messenger — Client, webhooks, commandes, commentaires, onboarding
"""

from .client import MessengerClient
from .commands import CommandRouter, get_contextual_quick_replies
from .comments import CommentsHandler

__all__ = ["MessengerClient", "CommandRouter", "get_contextual_quick_replies", "CommentsHandler"]
