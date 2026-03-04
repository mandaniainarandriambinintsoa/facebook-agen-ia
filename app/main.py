"""
Point d'entree principal de l'application FastAPI
Agent IA Facebook avec RAG — Multi-Tenant SaaS
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.config import settings
from app.facebook.webhooks import router as facebook_router


# Configuration du logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.debug else "INFO"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    logger.info("Demarrage de l'application Agent IA Facebook (SaaS Multi-Tenant)...")

    # Initialiser la base de donnees
    from app.db.database import init_db, close_db
    init_db()
    logger.info("Module base de donnees initialise")

    yield

    # Nettoyage
    await close_db()
    logger.info("Arret de l'application...")


# Creation de l'application FastAPI
app = FastAPI(
    title="Agent IA Facebook — SaaS Multi-Tenant",
    description="Plateforme SaaS pour chatbots IA Facebook avec RAG",
    version="2.0.0",
    lifespan=lifespan
)

# Configuration CORS (frontend Next.js sur Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ────────────────────────────────────────────────

# Facebook webhooks
app.include_router(facebook_router, prefix="/webhook", tags=["Facebook"])

# API routes (OAuth, tenants, catalog, analytics)
from app.api.tenants import router as auth_router, tenants_router
app.include_router(auth_router)
app.include_router(tenants_router)

from app.api.catalog import router as catalog_router
app.include_router(catalog_router)

from app.api.dashboard import router as dashboard_router
app.include_router(dashboard_router)


# ─── Health endpoints ─────────────────────────────────────

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "Agent IA Facebook — SaaS",
        "version": "2.0.0",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database_configured": bool(settings.database_url_async),
    }


@app.get("/api/config")
async def api_config():
    """Retourne la config publique"""
    return {
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "rag_top_k": settings.rag_top_k,
        "support_email": settings.support_email,
        "support_phone": settings.support_phone,
        "multi_tenant": bool(settings.database_url_async),
    }


@app.get("/api/debug/test-rag")
async def test_rag(q: str = "t-shirt"):
    """Endpoint de debug pour tester le pipeline RAG"""
    from app.db.database import AsyncSessionLocal
    from app.db import crud
    from app.rag.pg_retriever import PgVectorRetriever
    from app.rag.generator import ResponseGenerator
    from app.rag.confidence import ConfidenceHandler

    errors = []
    try:
        db = AsyncSessionLocal()
        # Trouver le premier tenant
        from sqlalchemy import select
        from app.db.models import Tenant
        result = await db.execute(select(Tenant).limit(1))
        tenant = result.scalar_one_or_none()
        if not tenant:
            return {"error": "No tenant found"}

        # Test retriever
        try:
            retriever = PgVectorRetriever(tenant_id=tenant.id, db=db)
            docs, score = await retriever.retrieve(q)
            errors.append(f"retriever OK: {len(docs)} docs, score={score:.3f}")
        except Exception as e:
            errors.append(f"retriever FAIL: {e}")
            await db.close()
            return {"errors": errors}

        # Test generator
        try:
            generator = ResponseGenerator()
            confidence = ConfidenceHandler()
            rag_response = await confidence.process_query_async(q, retriever, generator)
            errors.append(f"generator OK: {rag_response.response[:100]}")
        except Exception as e:
            errors.append(f"generator FAIL: {e}")

        await db.close()
        return {"steps": errors}
    except Exception as e:
        return {"error": str(e), "steps": errors}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
