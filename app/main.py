"""
Point d'entree principal de l'application FastAPI
Agent IA Facebook avec RAG
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
from pydantic import BaseModel
from typing import Optional
import sys

from pathlib import Path

from app.config import settings
from app.facebook.webhooks import router as facebook_router
from app.rag import RAGRetriever, ResponseGenerator, ConfidenceHandler
from app.knowledge.loader import DocumentLoader
from app.knowledge.processor import DocumentProcessor


# --- Schemas pour l'API n8n ---

class ChatRequest(BaseModel):
    """Requete entrante depuis n8n"""
    message: str
    sender_id: Optional[str] = None
    context: Optional[str] = None  # contexte additionnel (ex: nom page, type event)


class ChatResponse(BaseModel):
    """Reponse vers n8n"""
    response: str
    confidence_level: str
    confidence_score: float
    documents_used: int
    should_escalate: bool
    escalation_message: Optional[str] = None


# Configuration du logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.debug else "INFO"
)
logger.add(
    "logs/app.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG"
)


# Services globaux
rag_retriever: RAGRetriever | None = None
response_generator: ResponseGenerator | None = None
confidence_handler: ConfidenceHandler | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    global rag_retriever, response_generator, confidence_handler

    logger.info("Demarrage de l'application Agent IA Facebook...")

    # Initialisation des services RAG
    try:
        rag_retriever = RAGRetriever()
        response_generator = ResponseGenerator()
        confidence_handler = ConfidenceHandler()
        logger.info("Services RAG initialises avec succes")

        # Auto-indexation si la base est vide
        if len(rag_retriever.documents) == 0:
            logger.info("Base de connaissances vide, auto-indexation des documents...")
            _auto_index_documents(rag_retriever)
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des services RAG: {e}")
        raise

    yield

    # Nettoyage
    logger.info("Arret de l'application...")


# Creation de l'application FastAPI
app = FastAPI(
    title="Agent IA Facebook",
    description="Agent IA avec RAG pour repondre aux messages et commentaires Facebook",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes Facebook
app.include_router(facebook_router, prefix="/webhook", tags=["Facebook"])


@app.get("/")
async def root():
    """Endpoint de sante"""
    return {
        "status": "healthy",
        "service": "Agent IA Facebook",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Verification de l'etat de sante de l'application"""
    return {
        "status": "healthy",
        "rag_initialized": rag_retriever is not None,
        "generator_initialized": response_generator is not None
    }


def _auto_index_documents(retriever: RAGRetriever):
    """Indexe automatiquement les documents au demarrage si la base est vide"""
    documents_dir = Path("./data/documents")
    if not documents_dir.exists():
        logger.warning(f"Repertoire {documents_dir} introuvable, pas d'indexation")
        return

    loader = DocumentLoader(str(documents_dir))
    documents = loader.load_directory()

    if not documents:
        logger.warning("Aucun document trouve a indexer")
        return

    processor = DocumentProcessor(chunk_size=500, chunk_overlap=50, min_chunk_size=50)
    chunks = processor.process_documents(documents)
    docs, metadatas, ids = processor.prepare_for_indexing(chunks)

    retriever.add_documents(docs, metadatas, ids)
    logger.info(f"Auto-indexation terminee: {len(docs)} chunks indexes")


def get_rag_services():
    """Retourne les services RAG pour utilisation dans les handlers"""
    return {
        "retriever": rag_retriever,
        "generator": response_generator,
        "confidence": confidence_handler
    }


# --- API pour n8n ---

@app.post("/api/chat", response_model=ChatResponse)
async def api_chat(request: ChatRequest):
    """
    Endpoint principal pour n8n.
    Recoit un message, le traite via RAG, retourne la reponse.

    n8n envoie: {"message": "question de l'utilisateur"}
    On retourne: {"response": "...", "confidence_level": "high", ...}
    """
    if not rag_retriever or not response_generator or not confidence_handler:
        return ChatResponse(
            response=f"Service en cours de demarrage. Contactez {settings.support_email}.",
            confidence_level="none",
            confidence_score=0.0,
            documents_used=0,
            should_escalate=True,
            escalation_message="Services RAG non initialises"
        )

    try:
        rag_response = confidence_handler.process_query(
            query=request.message,
            retriever=rag_retriever,
            generator=response_generator
        )

        logger.info(
            f"API Chat - Query: '{request.message[:50]}...' | "
            f"Confidence: {rag_response.confidence_level.value} ({rag_response.confidence_score:.2f})"
        )

        return ChatResponse(
            response=rag_response.response,
            confidence_level=rag_response.confidence_level.value,
            confidence_score=round(rag_response.confidence_score, 3),
            documents_used=rag_response.documents_used,
            should_escalate=rag_response.should_escalate,
            escalation_message=rag_response.escalation_message
        )

    except Exception as e:
        logger.error(f"Erreur API Chat: {e}")
        return ChatResponse(
            response=f"Desolee, erreur technique. Contactez {settings.support_email}.",
            confidence_level="none",
            confidence_score=0.0,
            documents_used=0,
            should_escalate=True,
            escalation_message=str(e)
        )


@app.get("/api/config")
async def api_config():
    """Retourne la config publique (pour debug n8n)"""
    return {
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "rag_top_k": settings.rag_top_k,
        "rag_initialized": rag_retriever is not None,
        "documents_count": len(rag_retriever.documents) if rag_retriever else 0,
        "support_email": settings.support_email,
        "support_phone": settings.support_phone
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
