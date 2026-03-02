"""
Gestion de la confiance des reponses RAG
Determine si le systeme peut repondre ou doit escalader vers un humain
"""

from loguru import logger
from typing import List, Tuple
from dataclasses import dataclass
from enum import Enum

from app.config import settings
from app.rag.retriever import RetrievedDocument, RAGRetriever
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

    def process_query(
        self,
        query: str,
        retriever: RAGRetriever,
        generator: ResponseGenerator
    ) -> RAGResponse:
        """
        Traite une requete complete avec gestion de la confiance

        Args:
            query: Question de l'utilisateur
            retriever: Service de recherche
            generator: Service de generation

        Returns:
            RAGResponse avec la reponse et les metadonnees
        """
        # Etape 1: Recuperer les documents pertinents
        documents, avg_score = retriever.retrieve(query)

        # Etape 2: Determiner le niveau de confiance
        confidence_level = self._get_confidence_level(avg_score)

        logger.info(f"Query: '{query[:50]}...' | Score: {avg_score:.3f} | Level: {confidence_level.value}")

        # Etape 3: Decider de la reponse selon le niveau de confiance
        if confidence_level == ConfidenceLevel.NONE:
            # Confiance trop faible - escalader
            return RAGResponse(
                response=self._get_escalation_message(),
                confidence_level=confidence_level,
                confidence_score=avg_score,
                documents_used=0,
                should_escalate=True,
                escalation_message="Confiance trop faible pour repondre automatiquement"
            )

        elif confidence_level == ConfidenceLevel.LOW:
            # Confiance faible - repondre avec prudence + proposer escalade
            response = generator.generate_response(
                query=query,
                documents=documents,
                confidence_level="low"
            )
            return RAGResponse(
                response=response,
                confidence_level=confidence_level,
                confidence_score=avg_score,
                documents_used=len(documents),
                should_escalate=False,
                escalation_message="Proposition de contact support incluse"
            )

        elif confidence_level == ConfidenceLevel.MEDIUM:
            # Confiance moyenne - repondre avec mention du support
            response = generator.generate_response(
                query=query,
                documents=documents,
                confidence_level="medium"
            )
            return RAGResponse(
                response=response,
                confidence_level=confidence_level,
                confidence_score=avg_score,
                documents_used=len(documents),
                should_escalate=False
            )

        else:
            # Confiance haute - repondre directement
            response = generator.generate_response(
                query=query,
                documents=documents,
                confidence_level="high"
            )
            return RAGResponse(
                response=response,
                confidence_level=confidence_level,
                confidence_score=avg_score,
                documents_used=len(documents),
                should_escalate=False
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
