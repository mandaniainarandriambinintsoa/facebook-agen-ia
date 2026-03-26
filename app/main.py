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
from app.platforms.messenger.webhooks import router as webhook_router


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

    # Configurer le menu persistant pour les tenants Messenger actifs
    try:
        from app.db.database import AsyncSessionLocal
        if AsyncSessionLocal is not None:
            from sqlalchemy import select
            from app.db.models import TenantPlatform
            from app.platforms.messenger.client import MessengerClient

            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(TenantPlatform).where(
                        TenantPlatform.platform == "messenger",
                        TenantPlatform.is_active == True,
                    )
                )
                platforms = result.scalars().all()
                for tp in platforms:
                    client = MessengerClient(access_token=tp.access_token)
                    await client.setup_persistent_menu()
                    logger.info(f"Menu persistant configure pour {tp.platform_name}")
    except Exception as e:
        logger.warning(f"Erreur setup menu persistant au demarrage: {e}")

    yield

    # Nettoyage
    await close_db()
    logger.info("Arret de l'application...")


# Creation de l'application FastAPI
app = FastAPI(
    title="Agent IA Meta — SaaS Multi-Plateforme",
    description="Plateforme SaaS pour chatbots IA (Messenger, Instagram, WhatsApp) avec RAG",
    version="3.0.0",
    lifespan=lifespan
)

# Configuration CORS (frontend Next.js sur Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://facebook-dashboard-nine.vercel.app",
        "https://facebook-dashboard-mandas-projects-d5939030.vercel.app",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ────────────────────────────────────────────────

# Webhooks Meta (Facebook, Instagram, WhatsApp)
app.include_router(webhook_router, prefix="/webhook", tags=["Webhooks"])

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
        "service": "Agent IA Meta — SaaS Multi-Plateforme",
        "version": "3.0.0",
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
