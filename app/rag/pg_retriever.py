"""
PgVector Retriever — recherche vectorielle multi-tenant via PostgreSQL + pgvector
Meme interface que RAGRetriever mais filtre par tenant_id
"""

import uuid
from loguru import logger
from typing import List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.rag.embeddings import get_embedding_service
from app.rag.models import RetrievedDocument
from app.db import crud


class PgVectorRetriever:
    """
    Retriever multi-tenant utilisant pgvector.
    Chaque requete est filtree par tenant_id.
    """

    def __init__(self, tenant_id: uuid.UUID, db: AsyncSession):
        self.tenant_id = tenant_id
        self.db = db
        self.embedding_service = get_embedding_service()

    async def retrieve(
        self,
        query: str,
        top_k: int = None,
    ) -> Tuple[List[RetrievedDocument], float]:
        """
        Recherche les documents les plus pertinents pour ce tenant.

        Args:
            query: Question de l'utilisateur
            top_k: Nombre de documents a retourner

        Returns:
            Tuple (liste de RetrievedDocument, score moyen)
        """
        if top_k is None:
            top_k = settings.rag_top_k

        # Embed la requete
        query_vector = self.embedding_service.embed_text(query)

        # Recherche pgvector filtree par tenant
        rows = await crud.search_embeddings(
            db=self.db,
            tenant_id=self.tenant_id,
            query_vector=query_vector,
            top_k=top_k,
        )

        if not rows:
            logger.debug(f"Aucun document trouve pour tenant {self.tenant_id}")
            return [], 0.0

        documents = []
        scores = []
        for row in rows:
            doc = RetrievedDocument(
                content=row.content,
                metadata=row.metadata or {},
                score=float(row.score),
                id=str(row.id),
            )
            documents.append(doc)
            scores.append(doc.score)

        avg_score = sum(scores) / len(scores) if scores else 0.0
        logger.debug(
            f"PgVector query tenant={self.tenant_id}: "
            f"{len(documents)} docs, avg_score={avg_score:.3f}"
        )
        return documents, avg_score

    async def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict] = None,
    ) -> None:
        """
        Ajoute des documents avec leurs embeddings pour ce tenant.

        Args:
            documents: Textes a indexer
            metadatas: Metadonnees associees
        """
        if not documents:
            return

        if metadatas is None:
            metadatas = [{}] * len(documents)

        # Generer les embeddings en batch
        vectors = self.embedding_service.embed_texts(documents)

        await crud.add_embeddings(
            db=self.db,
            tenant_id=self.tenant_id,
            contents=documents,
            vectors=vectors,
            metadatas=metadatas,
        )
        logger.info(f"Tenant {self.tenant_id}: {len(documents)} documents indexes via pgvector")

    async def delete_all(self) -> None:
        """Supprime tous les embeddings de ce tenant"""
        await crud.delete_tenant_embeddings(self.db, self.tenant_id)
        logger.info(f"Tenant {self.tenant_id}: tous les embeddings supprimes")
