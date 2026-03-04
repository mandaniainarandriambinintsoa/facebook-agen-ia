"""
Gestion des tokens JWT
"""

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from loguru import logger

from app.config import settings


def create_access_token(data: dict) -> str:
    """Cree un token JWT"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiration_hours)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> dict | None:
    """Verifie et decode un token JWT. Retourne None si invalide."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as e:
        logger.debug(f"Token JWT invalide: {e}")
        return None
