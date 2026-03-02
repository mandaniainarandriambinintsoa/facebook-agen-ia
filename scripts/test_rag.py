#!/usr/bin/env python
"""
Script de test du systeme RAG
Permet de tester les reponses sans passer par Facebook
"""

import sys
from pathlib import Path

# Ajouter le repertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from app.rag.retriever import RAGRetriever
from app.rag.generator import ResponseGenerator
from app.rag.confidence import ConfidenceHandler


def test_single_query(query: str):
    """
    Teste une seule requete

    Args:
        query: Question a tester
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Question: {query}")
    logger.info("="*60)

    # Initialiser les services
    retriever = RAGRetriever()
    generator = ResponseGenerator()
    confidence = ConfidenceHandler()

    # Verifier si la base est vide
    stats = retriever.get_stats()
    if stats["document_count"] == 0:
        logger.warning("La base de connaissances est vide!")
        logger.info("Executez d'abord: python scripts/index_documents.py")
        return

    # Traiter la requete
    response = confidence.process_query(query, retriever, generator)

    # Afficher les resultats
    print(f"\n{'='*60}")
    print("RESULTAT:")
    print("="*60)
    print(f"\nNiveau de confiance: {response.confidence_level.value}")
    print(f"Score de confiance: {response.confidence_score:.3f}")
    print(f"Documents utilises: {response.documents_used}")
    print(f"Escalade necessaire: {response.should_escalate}")

    print(f"\n--- REPONSE ---")
    print(response.response)
    print("---")


def interactive_mode():
    """
    Mode interactif pour tester plusieurs questions
    """
    logger.info("\n=== Mode interactif RAG ===")
    logger.info("Tapez vos questions (ou 'quit' pour quitter)")
    logger.info("="*40)

    # Initialiser les services une seule fois
    retriever = RAGRetriever()
    generator = ResponseGenerator()
    confidence = ConfidenceHandler()

    # Verifier la base
    stats = retriever.get_stats()
    logger.info(f"Documents dans la base: {stats['document_count']}")

    if stats["document_count"] == 0:
        logger.warning("La base de connaissances est vide!")
        logger.info("Executez d'abord: python scripts/index_documents.py")
        return

    while True:
        try:
            query = input("\nVotre question: ").strip()

            if query.lower() in ["quit", "exit", "q"]:
                logger.info("Au revoir!")
                break

            if not query:
                continue

            # Traiter la requete
            response = confidence.process_query(query, retriever, generator)

            print(f"\n[Confiance: {response.confidence_level.value} ({response.confidence_score:.2f})]")
            print(f"\n{response.response}")

        except KeyboardInterrupt:
            logger.info("\nInterrompu par l'utilisateur")
            break
        except Exception as e:
            logger.error(f"Erreur: {e}")


def main():
    """
    Point d'entree principal
    """
    import argparse

    parser = argparse.ArgumentParser(description="Test du systeme RAG")
    parser.add_argument(
        "query",
        nargs="?",
        help="Question a tester (mode interactif si non fourni)"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Mode interactif"
    )

    args = parser.parse_args()

    if args.query:
        test_single_query(args.query)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
