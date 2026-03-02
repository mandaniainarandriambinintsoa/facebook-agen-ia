#!/usr/bin/env python
"""
Script d'indexation des documents dans la base de connaissances
Execute ce script pour charger vos documents dans ChromaDB
"""

import sys
from pathlib import Path

# Ajouter le repertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from app.knowledge.loader import DocumentLoader
from app.knowledge.processor import DocumentProcessor
from app.rag.retriever import RAGRetriever


def main():
    """
    Point d'entree principal pour l'indexation
    """
    logger.info("=== Debut de l'indexation des documents ===")

    # Configuration
    documents_dir = Path("./data/documents")

    # Creer le repertoire s'il n'existe pas
    documents_dir.mkdir(parents=True, exist_ok=True)

    # Verifier s'il y a des documents
    supported_files = list(documents_dir.rglob("*"))
    supported_files = [f for f in supported_files if f.suffix.lower() in {".pdf", ".txt", ".md", ".json"}]

    if not supported_files:
        logger.warning(f"Aucun document trouve dans {documents_dir}")
        logger.info("Formats supportes: .pdf, .txt, .md, .json")
        logger.info("Ajoutez vos documents dans le dossier data/documents/ puis relancez ce script")

        # Creer un fichier exemple
        create_example_documents(documents_dir)
        return

    logger.info(f"Documents trouves: {len(supported_files)}")
    for f in supported_files:
        logger.info(f"  - {f.name}")

    # Charger les documents
    loader = DocumentLoader(str(documents_dir))
    documents = loader.load_directory()

    if not documents:
        logger.warning("Aucun document charge")
        return

    logger.info(f"{len(documents)} documents charges")

    # Traiter les documents (chunking)
    processor = DocumentProcessor(
        chunk_size=500,
        chunk_overlap=50,
        min_chunk_size=100
    )
    chunks = processor.process_documents(documents)

    logger.info(f"{len(chunks)} chunks crees")

    # Preparer pour l'indexation
    docs, metadatas, ids = processor.prepare_for_indexing(chunks)

    # Indexer dans ChromaDB
    retriever = RAGRetriever()

    # Optionnel: supprimer les anciens documents
    logger.info("Suppression des anciens documents...")
    retriever.delete_all()

    # Ajouter les nouveaux documents
    logger.info("Indexation des documents...")
    retriever.add_documents(docs, metadatas, ids)

    # Afficher les statistiques
    stats = retriever.get_stats()
    logger.info("=== Indexation terminee ===")
    logger.info(f"Collection: {stats['collection_name']}")
    logger.info(f"Nombre de documents: {stats['document_count']}")
    logger.info(f"Modele d'embeddings: {stats['embedding_model']}")


def create_example_documents(documents_dir: Path):
    """
    Cree des documents d'exemple pour tester le systeme
    """
    logger.info("Creation de documents d'exemple...")

    # FAQ JSON exemple
    faq_content = """[
    {
        "question": "Quels sont vos horaires d'ouverture ?",
        "answer": "Nous sommes ouverts du lundi au vendredi de 9h a 18h, et le samedi de 10h a 16h. Nous sommes fermes le dimanche."
    },
    {
        "question": "Comment puis-je vous contacter ?",
        "answer": "Vous pouvez nous contacter par email a support@example.com ou par telephone au 01 23 45 67 89."
    },
    {
        "question": "Quelle est votre politique de retour ?",
        "answer": "Nous acceptons les retours dans les 30 jours suivant l'achat, a condition que le produit soit dans son emballage d'origine et non utilise."
    },
    {
        "question": "Proposez-vous la livraison gratuite ?",
        "answer": "Oui, la livraison est gratuite pour toute commande superieure a 50 euros. En dessous, les frais de livraison sont de 4,99 euros."
    },
    {
        "question": "Comment suivre ma commande ?",
        "answer": "Vous recevez un email avec un numero de suivi des que votre commande est expediee. Vous pouvez suivre votre colis sur notre site ou sur le site du transporteur."
    }
]"""

    faq_path = documents_dir / "faq_exemple.json"
    faq_path.write_text(faq_content, encoding="utf-8")
    logger.info(f"Fichier cree: {faq_path}")

    # Document texte exemple
    info_content = """Bienvenue sur notre boutique en ligne !

Qui sommes-nous ?
Nous sommes une entreprise specialisee dans la vente de produits de qualite depuis 2010.
Notre mission est de vous offrir les meilleurs produits au meilleur prix.

Nos services
- Livraison rapide sous 48h
- Service client disponible 6j/7
- Garantie satisfait ou rembourse
- Paiement securise

Nos engagements
Nous nous engageons a vous offrir une experience d'achat agreable et securisee.
Tous nos produits sont selectionnes avec soin et testes avant d'etre mis en vente.

Moyens de paiement acceptes
- Carte bancaire (Visa, Mastercard)
- PayPal
- Virement bancaire
- Paiement en 3 fois sans frais (pour les commandes > 100 euros)
"""

    info_path = documents_dir / "informations_entreprise.txt"
    info_path.write_text(info_content, encoding="utf-8")
    logger.info(f"Fichier cree: {info_path}")

    logger.info("Documents d'exemple crees. Relancez le script pour les indexer.")


if __name__ == "__main__":
    main()
