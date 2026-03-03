"""
Service d'embeddings pour la vectorisation des documents et requetes
Utilise fastembed (ONNX) pour des embeddings locaux legers sans PyTorch
"""

from fastembed import TextEmbedding
from loguru import logger
from typing import List
import numpy as np

from app.config import settings


class EmbeddingService:
    """Service de generation d'embeddings avec fastembed (ONNX)"""

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.embedding_model
        self._model = None
        logger.info(f"Service d'embeddings initialise avec le modele: {self.model_name}")

    @property
    def model(self) -> TextEmbedding:
        """Charge le modele de maniere lazy"""
        if self._model is None:
            logger.info(f"Chargement du modele d'embeddings: {self.model_name}")
            self._model = TextEmbedding(model_name=self.model_name)
            logger.info("Modele d'embeddings charge avec succes")
        return self._model

    def embed_text(self, text: str) -> List[float]:
        embeddings = list(self.model.embed([text]))
        return embeddings[0].tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        logger.debug(f"Generation d'embeddings pour {len(texts)} textes")
        embeddings = list(self.model.embed(texts))
        return [e.tolist() for e in embeddings]

    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
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
        return 384  # BAAI/bge-small-en-v1.5 et all-MiniLM-L6-v2 = 384 dims


# Instance globale du service d'embeddings
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Retourne l'instance globale du service d'embeddings"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
