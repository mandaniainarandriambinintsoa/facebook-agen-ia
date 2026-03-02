"""
RAG Retriever - Recherche semantique dans la base de connaissances
Utilise une base vectorielle simple en memoire avec numpy
"""

import json
import os
from loguru import logger
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
import numpy as np

from app.config import settings
from app.rag.embeddings import get_embedding_service, EmbeddingService


@dataclass
class RetrievedDocument:
    """Document recupere avec son score de similarite"""
    content: str
    metadata: Dict[str, Any]
    score: float
    id: str


class RAGRetriever:
    """
    Retriever pour la recherche semantique
    Utilise une base vectorielle simple en memoire avec numpy
    """

    def __init__(self):
        """Initialise le retriever"""
        self.embedding_service: EmbeddingService = get_embedding_service()

        # Stockage en memoire
        self.documents: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.ids: List[str] = []
        self.embeddings: np.ndarray | None = None

        # Repertoire de persistence
        self.persist_dir = settings.chroma_persist_directory
        os.makedirs(self.persist_dir, exist_ok=True)
        self.persist_file = os.path.join(self.persist_dir, "vector_store.json")
        self.embeddings_file = os.path.join(self.persist_dir, "embeddings.npy")

        # Charger les donnees existantes
        self._load_from_disk()

        logger.info(f"RAG Retriever initialise. Documents: {len(self.documents)}")

    def _load_from_disk(self) -> None:
        """Charge les donnees depuis le disque"""
        try:
            if os.path.exists(self.persist_file) and os.path.exists(self.embeddings_file):
                with open(self.persist_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.documents = data.get("documents", [])
                    self.metadatas = data.get("metadatas", [])
                    self.ids = data.get("ids", [])

                self.embeddings = np.load(self.embeddings_file)
                logger.info(f"Donnees chargees: {len(self.documents)} documents")
        except Exception as e:
            logger.warning(f"Impossible de charger les donnees: {e}")
            self.documents = []
            self.metadatas = []
            self.ids = []
            self.embeddings = None

    def _save_to_disk(self) -> None:
        """Sauvegarde les donnees sur le disque"""
        try:
            data = {
                "documents": self.documents,
                "metadatas": self.metadatas,
                "ids": self.ids
            }
            with open(self.persist_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            if self.embeddings is not None:
                np.save(self.embeddings_file, self.embeddings)

            logger.debug("Donnees sauvegardees sur le disque")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]] | None = None,
        ids: List[str] | None = None
    ) -> None:
        """
        Ajoute des documents a la base de connaissances

        Args:
            documents: Liste de textes a ajouter
            metadatas: Metadonnees associees (source, type, etc.)
            ids: Identifiants uniques des documents
        """
        if not documents:
            logger.warning("Aucun document a ajouter")
            return

        # Generer les IDs si non fournis
        if ids is None:
            existing_count = len(self.documents)
            ids = [f"doc_{existing_count + i}" for i in range(len(documents))]

        # Generer les metadonnees par defaut si non fournies
        if metadatas is None:
            metadatas = [{"source": "unknown"} for _ in documents]

        # Generer les embeddings
        new_embeddings = self.embedding_service.embed_texts(documents)
        new_embeddings_array = np.array(new_embeddings)

        # Ajouter aux listes existantes
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)
        self.ids.extend(ids)

        # Combiner les embeddings
        if self.embeddings is None:
            self.embeddings = new_embeddings_array
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings_array])

        # Sauvegarder
        self._save_to_disk()

        logger.info(f"{len(documents)} documents ajoutes a la base de connaissances")

    def _cosine_similarity(self, query_embedding: np.ndarray, doc_embeddings: np.ndarray) -> np.ndarray:
        """
        Calcule la similarite cosinus entre une requete et tous les documents

        Args:
            query_embedding: Embedding de la requete (1D)
            doc_embeddings: Embeddings des documents (2D)

        Returns:
            Array des scores de similarite
        """
        # Normaliser
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        doc_norms = doc_embeddings / np.linalg.norm(doc_embeddings, axis=1, keepdims=True)

        # Produit scalaire = similarite cosinus pour vecteurs normalises
        similarities = np.dot(doc_norms, query_norm)

        return similarities

    def retrieve(
        self,
        query: str,
        top_k: int | None = None
    ) -> Tuple[List[RetrievedDocument], float]:
        """
        Recherche les documents les plus pertinents pour une requete

        Args:
            query: Question ou requete de l'utilisateur
            top_k: Nombre de documents a retourner

        Returns:
            Tuple (liste de documents, score moyen de confiance)
        """
        if top_k is None:
            top_k = settings.rag_top_k

        # Verifier si la base est vide
        if not self.documents or self.embeddings is None:
            logger.warning("La base de connaissances est vide")
            return [], 0.0

        # Generer l'embedding de la requete
        query_embedding = np.array(self.embedding_service.embed_text(query))

        # Calculer les similarites
        similarities = self._cosine_similarity(query_embedding, self.embeddings)

        # Obtenir les top-k indices
        top_k = min(top_k, len(self.documents))
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        # Construire les resultats
        documents = []
        scores = []

        for idx in top_indices:
            score = float(similarities[idx])
            retrieved_doc = RetrievedDocument(
                content=self.documents[idx],
                metadata=self.metadatas[idx],
                score=score,
                id=self.ids[idx]
            )
            documents.append(retrieved_doc)
            scores.append(score)

        # Calculer le score moyen
        avg_score = sum(scores) / len(scores) if scores else 0.0

        logger.debug(f"Requete: '{query[:50]}...' - {len(documents)} documents, score moyen: {avg_score:.3f}")

        return documents, avg_score

    def delete_all(self) -> None:
        """Supprime tous les documents de la collection"""
        self.documents = []
        self.metadatas = []
        self.ids = []
        self.embeddings = None

        # Supprimer les fichiers
        if os.path.exists(self.persist_file):
            os.remove(self.persist_file)
        if os.path.exists(self.embeddings_file):
            os.remove(self.embeddings_file)

        logger.info("Tous les documents ont ete supprimes")

    def get_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur la base de connaissances"""
        return {
            "collection_name": "vector_store",
            "document_count": len(self.documents),
            "embedding_model": settings.embedding_model
        }
