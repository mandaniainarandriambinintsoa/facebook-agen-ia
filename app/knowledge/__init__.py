"""
Module de gestion des connaissances
Chargement et traitement des documents multi-sources
"""

from .loader import DocumentLoader
from .processor import DocumentProcessor

__all__ = ["DocumentLoader", "DocumentProcessor"]
