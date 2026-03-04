"""
Configuration de la base de donnees
AsyncEngine (asyncpg) + session factory
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from loguru import logger

from app.config import settings


class Base(DeclarativeBase):
    pass


# Engine async (asyncpg)
engine = None
AsyncSessionLocal = None


def init_db():
    """Initialise le moteur de base de donnees"""
    global engine, AsyncSessionLocal

    if not settings.database_url_async:
        logger.warning("DATABASE_URL_ASYNC non configuree — mode BDD desactive")
        return

    # asyncpg n'accepte pas ?sslmode=require, il faut le convertir en ?ssl=require
    db_url = settings.database_url_async.replace("sslmode=", "ssl=")

    engine = create_async_engine(
        db_url,
        echo=settings.debug,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )

    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    logger.info("Moteur de base de donnees initialise")


async def get_db():
    """Dependency FastAPI pour obtenir une session DB"""
    if AsyncSessionLocal is None:
        raise RuntimeError("Base de donnees non initialisee. Verifiez DATABASE_URL_ASYNC.")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def close_db():
    """Ferme le moteur de base de donnees"""
    global engine
    if engine:
        await engine.dispose()
        logger.info("Moteur de base de donnees ferme")
