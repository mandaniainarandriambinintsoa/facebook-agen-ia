"""
Service d'embeddings pour la vectorisation des documents et requetes
Utilise sentence-transformers pour des embeddings locaux gratuits
"""

from sentence_transformers import SentenceTransformer
from loguru import logger
from typing import List
import numpy as np

from app.config import settings


class EmbeddingService:
    """Service de generation d'embeddings avec sentence-transformers"""

    def __init__(self, model_name: str | None = None):
        """
        Initialise le service d'embeddings

        Args:
            model_name: Nom du modele sentence-transformers (optionnel)
        """
        self.model_name = model_name or settings.embedding_model
        self._model = None
        logger.info(f"Service d'embeddings initialise avec le modele: {self.model_name}")

    @property
    def model(self) -> SentenceTransformer:
        """Charge le modele de maniere lazy"""
        if self._model is None:
            logger.info(f"Chargement du modele d'embeddings: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            logger.info("Modele d'embeddings charge avec succes")
        return self._model

    def embed_text(self, text: str) -> List[float]:
        """
        Genere un embedding pour un texte unique

        Args:
            text: Texte a vectoriser

        Returns:
            Liste de floats representant l'embedding
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Genere des embeddings pour une liste de textes

        Args:
            texts: Liste de textes a vectoriser

        Returns:
            Liste d'embeddings
        """
        if not texts:
            return []

        logger.debug(f"Generation d'embeddings pour {len(texts)} textes")
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=len(texts) > 10)
        return embeddings.tolist()

    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calcule la similarite cosinus entre deux embeddings

        Args:
            embedding1: Premier embedding
            embedding2: Second embedding

        Returns:
            Score de similarite entre 0 et 1
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    @property
    def embedding_dimension(self) -> int:
        """Retourne la dimension des embeddings"""
        return self.model.get_sentence_embedding_dimension()


# Instance globale du service d'embeddings
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Retourne l'instance globale du service d'embeddings"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
