"""
Service d'embeddings pour la vectorisation des documents et requetes
Utilise fastembed (ONNX) pour des embeddings locaux legers sans PyTorch.

Support des modeles E5 multilingues (intfloat/multilingual-e5-*) qui exigent
des prefixes "query: " et "passage: " pour optimiser le retrieval. Detection
automatique du type de modele via model_name.
"""

from fastembed import TextEmbedding
from loguru import logger
from typing import List
import numpy as np

from app.config import settings


def _is_e5_model(model_name: str) -> bool:
    """Detecte si le modele est de la famille E5 (intfloat/multilingual-e5-*)."""
    return "e5" in model_name.lower()


class EmbeddingService:
    """Service de generation d'embeddings avec fastembed (ONNX)"""

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.embedding_model
        self._model = None
        self._is_e5 = _is_e5_model(self.model_name)
        logger.debug(
            f"Service d'embeddings initialise avec le modele: {self.model_name} "
            f"(E5 prefixes: {self._is_e5})"
        )

    @property
    def model(self) -> TextEmbedding:
        """Charge le modele de maniere lazy"""
        if self._model is None:
            logger.info(f"Chargement initial du modele d'embeddings: {self.model_name}")
            try:
                self._model = TextEmbedding(model_name=self.model_name)
            except ValueError as e:
                # Fastembed ne supporte pas le modele demande. Loguer la liste des
                # modeles supportes pour diagnostic rapide cote ops.
                try:
                    supported = [m["model"] for m in TextEmbedding.list_supported_models()]
                except Exception:
                    supported = ["(impossible de lister les modeles supportes)"]
                logger.error(
                    f"Modele '{self.model_name}' non supporte par fastembed. "
                    f"Modeles disponibles dans cette version: {supported}"
                )
                raise
            logger.info("Modele d'embeddings charge avec succes")
        return self._model

    def _prepare_query(self, text: str) -> str:
        """Applique le prefixe 'query: ' si modele E5, sinon retourne le texte brut."""
        if self._is_e5:
            return f"query: {text}"
        return text

    def _prepare_passage(self, text: str) -> str:
        """Applique le prefixe 'passage: ' si modele E5, sinon retourne le texte brut."""
        if self._is_e5:
            return f"passage: {text}"
        return text

    def embed_text(self, text: str) -> List[float]:
        """Embed une query (recherche). Applique le prefixe 'query: ' si E5."""
        prepared = self._prepare_query(text)
        embeddings = list(self.model.embed([prepared]))
        return embeddings[0].tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed des passages (documents a indexer). Applique 'passage: ' si E5."""
        if not texts:
            return []
        logger.debug(f"Generation d'embeddings pour {len(texts)} textes")
        prepared = [self._prepare_passage(t) for t in texts]
        embeddings = list(self.model.embed(prepared))
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
        # bge-small-en-v1.5, all-MiniLM-L6-v2, multilingual-e5-small = 384 dims
        return 384


# Instance globale du service d'embeddings
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Retourne l'instance globale du service d'embeddings"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
