"""
Processeur de documents
Decoupe les documents en chunks et les prepare pour l'indexation
"""

from loguru import logger
from typing import List, Dict, Any
from dataclasses import dataclass
import re

from app.knowledge.loader import Document


@dataclass
class ProcessedChunk:
    """Chunk de document traite"""
    content: str
    metadata: Dict[str, Any]
    chunk_index: int
    total_chunks: int


class DocumentProcessor:
    """
    Processeur de documents pour le RAG
    Decoupe en chunks avec overlap pour une meilleure recherche
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        min_chunk_size: int = 100
    ):
        """
        Initialise le processeur

        Args:
            chunk_size: Taille maximale d'un chunk en caracteres
            chunk_overlap: Chevauchement entre chunks
            min_chunk_size: Taille minimale d'un chunk
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        logger.info(f"DocumentProcessor initialise: chunk_size={chunk_size}, overlap={chunk_overlap}")

    def _clean_text(self, text: str) -> str:
        """Nettoie un texte"""
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        # Supprimer les lignes vides multiples
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()

    def _split_into_sentences(self, text: str) -> List[str]:
        """Decoupe un texte en phrases"""
        # Pattern simple pour decouper en phrases
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _create_chunks(self, text: str) -> List[str]:
        """
        Decoupe un texte en chunks avec overlap

        Args:
            text: Texte a decouper

        Returns:
            Liste de chunks
        """
        text = self._clean_text(text)

        if len(text) <= self.chunk_size:
            return [text] if len(text) >= self.min_chunk_size else []

        chunks = []
        sentences = self._split_into_sentences(text)

        current_chunk = ""
        for sentence in sentences:
            # Si ajouter cette phrase depasse la taille
            if len(current_chunk) + len(sentence) + 1 > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())

                # Commencer un nouveau chunk avec overlap
                if self.chunk_overlap > 0 and chunks:
                    # Prendre la fin du chunk precedent comme overlap
                    overlap_text = chunks[-1][-self.chunk_overlap:]
                    current_chunk = overlap_text + " " + sentence
                else:
                    current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence

        # Ajouter le dernier chunk
        if current_chunk and len(current_chunk.strip()) >= self.min_chunk_size:
            chunks.append(current_chunk.strip())

        return chunks

    def process_document(self, document: Document) -> List[ProcessedChunk]:
        """
        Traite un document et le decoupe en chunks

        Args:
            document: Document a traiter

        Returns:
            Liste de chunks traites
        """
        chunks_text = self._create_chunks(document.content)

        processed_chunks = []
        for i, chunk_content in enumerate(chunks_text):
            processed_chunk = ProcessedChunk(
                content=chunk_content,
                metadata={
                    **document.metadata,
                    "source": document.source,
                    "doc_type": document.doc_type,
                    "chunk_index": i,
                    "total_chunks": len(chunks_text)
                },
                chunk_index=i,
                total_chunks=len(chunks_text)
            )
            processed_chunks.append(processed_chunk)

        return processed_chunks

    def process_documents(self, documents: List[Document]) -> List[ProcessedChunk]:
        """
        Traite une liste de documents

        Args:
            documents: Liste de documents a traiter

        Returns:
            Liste de tous les chunks
        """
        all_chunks = []

        for doc in documents:
            chunks = self.process_document(doc)
            all_chunks.extend(chunks)

        logger.info(f"{len(documents)} documents traites -> {len(all_chunks)} chunks")
        return all_chunks

    def prepare_for_indexing(self, chunks: List[ProcessedChunk]) -> tuple:
        """
        Prepare les chunks pour l'indexation dans ChromaDB

        Args:
            chunks: Liste de chunks traites

        Returns:
            Tuple (documents, metadatas, ids)
        """
        documents = []
        metadatas = []
        ids = []

        for i, chunk in enumerate(chunks):
            documents.append(chunk.content)

            # S'assurer que les metadonnees sont serialisables
            clean_metadata = {}
            for key, value in chunk.metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    clean_metadata[key] = value
                else:
                    clean_metadata[key] = str(value)

            metadatas.append(clean_metadata)
            ids.append(f"chunk_{i}_{hash(chunk.content) % 10000}")

        return documents, metadatas, ids
