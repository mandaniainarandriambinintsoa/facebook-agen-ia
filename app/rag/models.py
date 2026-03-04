"""
Modeles partages pour le module RAG
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class RetrievedDocument:
    """Document recupere avec son score de similarite"""
    content: str
    metadata: Dict[str, Any]
    score: float
    id: str
