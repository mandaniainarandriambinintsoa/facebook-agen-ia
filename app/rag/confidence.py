"""
Gestion de la confiance des reponses RAG
Determine si le systeme peut repondre ou doit escalader vers un humain
"""

from loguru import logger
from typing import List, Tuple
from dataclasses import dataclass
from enum import Enum

from app.config import settings
from app.rag.models import RetrievedDocument
from app.rag.generator import ResponseGenerator


class ConfidenceLevel(Enum):
    """Niveaux de confiance pour les reponses"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


@dataclass
class RAGResponse:
    """Reponse complete du systeme RAG"""
    response: str
    confidence_level: ConfidenceLevel
    confidence_score: float
    documents_used: int
    should_escalate: bool
    escalation_message: str | None = None
    top_document: RetrievedDocument | None = None


class ConfidenceHandler:
    """
    Gestionnaire de confiance pour les reponses RAG
    Decide si le systeme peut repondre ou doit escalader
    """

    def __init__(self):
        """Initialise les seuils de confiance"""
        self.high_threshold = settings.rag_confidence_high
        self.medium_threshold = settings.rag_confidence_medium
        self.low_threshold = settings.rag_confidence_low

        logger.info(f"Seuils de confiance: high={self.high_threshold}, "
                   f"medium={self.medium_threshold}, low={self.low_threshold}")

    def _get_confidence_level(self, score: float) -> ConfidenceLevel:
        """Determine le niveau de confiance a partir du score"""
        if score >= self.high_threshold:
            return ConfidenceLevel.HIGH
        elif score >= self.medium_threshold:
            return ConfidenceLevel.MEDIUM
        elif score >= self.low_threshold:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.NONE

    def _get_escalation_message(self) -> str:
        """Message d'escalation vers un humain"""
        contacts = []
        if settings.support_email:
            contacts.append(f"email: {settings.support_email}")
        if settings.support_phone:
            contacts.append(f"telephone: {settings.support_phone}")

        contact_str = " ou ".join(contacts) if contacts else "notre equipe"

        return (
            "Je n'ai pas suffisamment d'informations pour repondre precisement a votre question. "
            f"Pour une assistance personnalisee, vous pouvez contacter {contact_str}. "
            "Un conseiller sera ravi de vous aider !"
        )

    async def process_query_async(
        self,
        query: str,
        retriever,
        generator: ResponseGenerator,
        chat_history: list[dict] | None = None,
    ) -> RAGResponse:
        """
        Version async de process_query pour le PgVectorRetriever.
        Le retriever doit avoir une methode retrieve() async.

        chat_history: historique conversationnel chronologique
            [{"role": "user"|"assistant", "content": str}, ...]
            sert a (1) augmenter la requete RAG pour capturer les references
            implicites ("noir" apres "casquette" → retrieve sur "casquette noir"),
            et (2) est passe au generator pour que le LLM comprenne le contexte.
        """
        # Augmentation de la requete RAG : concatener les derniers messages user
        # pour que la similarite vectorielle capture le vrai sujet.
        augmented_query = query
        if chat_history:
            recent_user = [
                t["content"].strip()
                for t in chat_history[-6:]
                if t.get("role") == "user" and (t.get("content") or "").strip()
            ][-2:]
            if recent_user:
                augmented_query = " ".join(recent_user + [query])

        documents, avg_score = await retriever.retrieve(augmented_query)
        confidence_level = self._get_confidence_level(avg_score)

        logger.info(
            f"Query: '{query[:50]}...' | Augmented: '{augmented_query[:60]}...' | "
            f"Score: {avg_score:.3f} | Level: {confidence_level.value}"
        )

        top_doc = documents[0] if documents else None

        # On appelle toujours le LLM, meme en confiance NONE :
        # le system prompt (par defaut ou custom) sait gerer les requetes vagues
        # comme "bonjour", "ok", "merci" avec une reponse polie.
        # Ne jamais injecter un message hardcode avec les env support_email/phone
        # car ca leak des valeurs placeholder et ignore le prompt custom du tenant.
        response = generator.generate_response(
            query=query,
            documents=documents,
            confidence_level=confidence_level.value,
            chat_history=chat_history,
        )
        return RAGResponse(
            response=response,
            confidence_level=confidence_level,
            confidence_score=avg_score,
            documents_used=len(documents),
            should_escalate=(confidence_level == ConfidenceLevel.NONE),
            escalation_message=(
                "Confiance RAG tres faible" if confidence_level == ConfidenceLevel.NONE
                else "Proposition de contact support incluse" if confidence_level == ConfidenceLevel.LOW
                else None
            ),
            top_document=top_doc,
        )

    def should_respond(self, score: float) -> bool:
        """Verifie si le systeme devrait repondre automatiquement"""
        return score >= self.low_threshold

    def get_confidence_stats(self, score: float) -> dict:
        """Retourne des statistiques sur la confiance"""
        level = self._get_confidence_level(score)
        return {
            "score": score,
            "level": level.value,
            "can_respond": self.should_respond(score),
            "thresholds": {
                "high": self.high_threshold,
                "medium": self.medium_threshold,
                "low": self.low_threshold
            }
        }
