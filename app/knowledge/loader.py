"""
Chargeur de documents multi-sources
Supporte PDFs, fichiers texte, markdown, et pages web
"""

from pathlib import Path
from loguru import logger
from typing import List, Dict, Any, Generator
from dataclasses import dataclass
import os


@dataclass
class Document:
    """Represente un document charge"""
    content: str
    metadata: Dict[str, Any]
    source: str
    doc_type: str


class DocumentLoader:
    """
    Chargeur de documents multi-sources
    Supporte: PDF, TXT, MD, JSON, et scraping web
    """

    SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".json", ".csv"}

    def __init__(self, documents_dir: str = "./data/documents"):
        """
        Initialise le chargeur de documents

        Args:
            documents_dir: Repertoire contenant les documents
        """
        self.documents_dir = Path(documents_dir)
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"DocumentLoader initialise. Repertoire: {self.documents_dir}")

    def load_pdf(self, file_path: Path) -> List[Document]:
        """Charge un fichier PDF"""
        documents = []
        try:
            import pdfplumber

            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        documents.append(Document(
                            content=text.strip(),
                            metadata={
                                "page": i + 1,
                                "total_pages": len(pdf.pages),
                                "filename": file_path.name
                            },
                            source=str(file_path),
                            doc_type="pdf"
                        ))

            logger.info(f"PDF charge: {file_path.name} - {len(documents)} pages")

        except ImportError:
            logger.warning("pdfplumber non installe, essai avec PyPDF2")
            try:
                from PyPDF2 import PdfReader

                reader = PdfReader(str(file_path))
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        documents.append(Document(
                            content=text.strip(),
                            metadata={
                                "page": i + 1,
                                "total_pages": len(reader.pages),
                                "filename": file_path.name
                            },
                            source=str(file_path),
                            doc_type="pdf"
                        ))

                logger.info(f"PDF charge (PyPDF2): {file_path.name} - {len(documents)} pages")

            except Exception as e:
                logger.error(f"Erreur chargement PDF {file_path}: {e}")

        except Exception as e:
            logger.error(f"Erreur chargement PDF {file_path}: {e}")

        return documents

    def load_text(self, file_path: Path) -> List[Document]:
        """Charge un fichier texte ou markdown"""
        documents = []
        try:
            content = file_path.read_text(encoding="utf-8")
            if content.strip():
                documents.append(Document(
                    content=content.strip(),
                    metadata={
                        "filename": file_path.name,
                        "extension": file_path.suffix
                    },
                    source=str(file_path),
                    doc_type="text"
                ))
                logger.info(f"Fichier texte charge: {file_path.name}")

        except Exception as e:
            logger.error(f"Erreur chargement texte {file_path}: {e}")

        return documents

    def load_json_faq(self, file_path: Path) -> List[Document]:
        """
        Charge un fichier JSON (FAQ ou catalogue produits)
        Formats supportes:
        - FAQ: [{"question": "...", "answer": "..."}]
        - Catalogue: [{"categorie": "...", "produits": [...]}]
        """
        documents = []
        try:
            import json

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        # Format FAQ
                        question = item.get("question", item.get("q", ""))
                        answer = item.get("answer", item.get("a", item.get("response", "")))

                        if question and answer:
                            content = f"Question: {question}\nReponse: {answer}"
                            documents.append(Document(
                                content=content,
                                metadata={
                                    "question": question,
                                    "index": i,
                                    "filename": file_path.name
                                },
                                source=str(file_path),
                                doc_type="faq"
                            ))

                        # Format catalogue produits
                        elif "categorie" in item and "produits" in item:
                            categorie = item["categorie"]
                            for produit in item["produits"]:
                                nom = produit.get("nom", "")
                                prix = produit.get("prix", "")
                                tailles = produit.get("tailles", "")
                                couleurs = produit.get("couleurs", "")
                                stock = produit.get("stock", "")

                                content = (
                                    f"Produit: {nom}\n"
                                    f"Categorie: {categorie}\n"
                                    f"Prix: {prix}\n"
                                    f"Tailles disponibles: {tailles}\n"
                                    f"Couleurs: {couleurs}\n"
                                    f"Disponibilite: {stock}"
                                )
                                documents.append(Document(
                                    content=content,
                                    metadata={
                                        "categorie": categorie,
                                        "produit": nom,
                                        "prix": prix,
                                        "stock": stock,
                                        "filename": file_path.name
                                    },
                                    source=str(file_path),
                                    doc_type="catalogue"
                                ))

            logger.info(f"JSON charge: {file_path.name} - {len(documents)} elements")

        except Exception as e:
            logger.error(f"Erreur chargement JSON {file_path}: {e}")

        return documents

    def load_from_url(self, url: str) -> List[Document]:
        """Charge le contenu d'une page web"""
        documents = []
        try:
            import httpx
            from bs4 import BeautifulSoup

            response = httpx.get(url, timeout=30, follow_redirects=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Supprimer les scripts et styles
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            # Extraire le texte
            text = soup.get_text(separator="\n", strip=True)

            if text:
                # Nettoyer le texte
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                content = "\n".join(lines)

                documents.append(Document(
                    content=content[:10000],  # Limiter la taille
                    metadata={
                        "url": url,
                        "title": soup.title.string if soup.title else ""
                    },
                    source=url,
                    doc_type="web"
                ))
                logger.info(f"Page web chargee: {url}")

        except Exception as e:
            logger.error(f"Erreur chargement URL {url}: {e}")

        return documents

    def load_file(self, file_path: Path) -> List[Document]:
        """Charge un fichier selon son extension"""
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return self.load_pdf(file_path)
        elif suffix in {".txt", ".md"}:
            return self.load_text(file_path)
        elif suffix == ".json":
            return self.load_json_faq(file_path)
        else:
            logger.warning(f"Extension non supportee: {suffix}")
            return []

    def load_directory(self, directory: Path | None = None) -> List[Document]:
        """
        Charge tous les documents d'un repertoire

        Args:
            directory: Repertoire a charger (defaut: self.documents_dir)

        Returns:
            Liste de tous les documents charges
        """
        if directory is None:
            directory = self.documents_dir

        documents = []

        if not directory.exists():
            logger.warning(f"Repertoire inexistant: {directory}")
            return documents

        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                docs = self.load_file(file_path)
                documents.extend(docs)

        logger.info(f"Total documents charges: {len(documents)}")
        return documents

    def load_from_sources(self, sources: List[Dict[str, str]]) -> List[Document]:
        """
        Charge depuis une liste de sources mixtes

        Args:
            sources: Liste de {"type": "file|url|directory", "path": "..."}

        Returns:
            Liste de documents
        """
        documents = []

        for source in sources:
            source_type = source.get("type", "file")
            path = source.get("path", "")

            if source_type == "url":
                docs = self.load_from_url(path)
            elif source_type == "directory":
                docs = self.load_directory(Path(path))
            else:
                docs = self.load_file(Path(path))

            documents.extend(docs)

        return documents
