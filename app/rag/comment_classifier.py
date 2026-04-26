"""
Classifier d'intent pour commentaires Facebook
Decide si on engage l'auteur en DM ou si on ignore
"""

import json
from loguru import logger
from typing import Literal, TypedDict

from app.config import settings


CommentIntent = Literal[
    "price",          # demande de prix
    "details",        # demande de details (taille, couleur, dispo, livraison...)
    "mp_request",     # "mp", "inbox", "DM", "prive"
    "question_other", # autre question
    "compliment",     # "bon produit", emoji positif
    "tag_friend",     # mention d'un ami sans question
    "spam",           # promo / lien / repetition
    "insult",         # insulte / negatif sans demande
    "other",
]


class CommentClassification(TypedDict):
    engage: bool
    intent: CommentIntent
    language: str  # "fr" | "mg" | "mixed" | "other"
    confidence: float  # 0.0 - 1.0


SYSTEM_PROMPT = """Tu es un classifier de commentaires Facebook pour une page e-commerce/service. Tu decides si on doit engager l'auteur en message prive (DM) ou non.

REGLES STRICTES :
- engage=true UNIQUEMENT si le commentaire contient une demande de contact, une question sur le produit, le prix, les details, la dispo, la livraison, OU une demande explicite de MP/inbox/DM/prive.
- engage=false pour : compliments simples ("bon produit", "tena tsara", emoji seul), tags d'amis sans question, spam, insultes, ou commentaires sans intention claire.

INTENTS :
- price : demande de prix ("combien ?", "prix svp", "ohatrinona")
- details : demande de details produit (taille, couleur, dispo, livraison, matiere)
- mp_request : "mp", "inbox", "dm", "prive" mentionne
- question_other : toute autre question concrete
- compliment : eloge sans question ("super", "j'aime", "tena tsara")
- tag_friend : juste un @ami sans contenu
- spam : promo / lien externe / repetition
- insult : negatif / hostile sans demande
- other : ne rentre dans aucune categorie

Tu retournes UNIQUEMENT un JSON valide avec ces champs :
{"engage": bool, "intent": "<intent>", "language": "fr"|"mg"|"mixed"|"other", "confidence": float}"""


class CommentClassifier:
    """Classifier LLM pour decider d'engager ou non sur un commentaire FB"""

    def __init__(self):
        self.client = None
        self.model = "gpt-4o-mini"
        self._init_client()

    def _init_client(self):
        provider = settings.llm_provider
        try:
            if provider == "openai" and settings.openai_api_key:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.openai_api_key)
                self.model = settings.llm_model or "gpt-4o-mini"
            elif provider == "groq" and settings.groq_api_key:
                from groq import Groq
                self.client = Groq(api_key=settings.groq_api_key)
                self.model = settings.groq_model or "llama-3.3-70b-versatile"
            elif settings.openai_api_key:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.openai_api_key)
                self.model = "gpt-4o-mini"
            elif settings.groq_api_key:
                from groq import Groq
                self.client = Groq(api_key=settings.groq_api_key)
                self.model = settings.groq_model or "llama-3.3-70b-versatile"
        except Exception as e:
            logger.error(f"CommentClassifier: init client erreur: {e}")

    def classify(self, comment_text: str) -> CommentClassification:
        """
        Classifie un commentaire FB. Retourne toujours un dict valide
        meme en cas d'erreur (fallback engage=false).
        """
        fallback: CommentClassification = {
            "engage": False,
            "intent": "other",
            "language": "fr",
            "confidence": 0.0,
        }

        if not self.client or not comment_text or len(comment_text.strip()) < 1:
            return fallback

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Commentaire: \"{comment_text.strip()[:500]}\""},
                ],
                response_format={"type": "json_object"},
                max_tokens=150,
                temperature=0.1,
            )
            raw = response.choices[0].message.content or "{}"
            data = json.loads(raw)
            return {
                "engage": bool(data.get("engage", False)),
                "intent": data.get("intent", "other"),
                "language": data.get("language", "fr"),
                "confidence": float(data.get("confidence", 0.0)),
            }
        except Exception as e:
            logger.error(f"CommentClassifier: erreur classification: {e}")
            return fallback
