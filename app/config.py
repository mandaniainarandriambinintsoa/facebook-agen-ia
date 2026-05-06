"""
Configuration de l'application
Charge les variables d'environnement et definit les parametres
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import Literal


class Settings(BaseSettings):
    """Configuration principale de l'application"""

    # Facebook Configuration
    facebook_app_id: str = Field(default="", description="Facebook App ID")
    facebook_app_secret: str = Field(default="", description="Facebook App Secret")
    facebook_page_access_token: str = Field(default="", description="Page Access Token")
    facebook_verify_token: str = Field(default="fb_verify_token_123", description="Webhook Verify Token")

    # LLM Configuration
    anthropic_api_key: str = Field(default="", description="Anthropic API Key")
    openai_api_key: str = Field(default="", description="OpenAI API Key")
    groq_api_key: str = Field(default="", description="Groq API Key")
    llm_provider: Literal["anthropic", "openai", "groq"] = Field(default="groq", description="LLM Provider principal")
    llm_model: str = Field(default="llama-3.3-70b-versatile", description="LLM Model")
    groq_model: str = Field(default="llama-3.3-70b-versatile", description="Groq fallback model")

    # n8n Configuration
    n8n_base_url: str = Field(default="", description="n8n instance URL")

    # Database Configuration (Neon PostgreSQL + pgvector)
    database_url: str = Field(default="", description="PostgreSQL URL (sync, for Alembic)")
    database_url_async: str = Field(default="", description="PostgreSQL URL (async, asyncpg)")

    # Multi-tenant / SaaS Configuration
    jwt_secret: str = Field(default="change-me-in-production", description="JWT signing secret")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_hours: int = Field(default=72, description="JWT token expiration in hours")
    facebook_oauth_redirect_uri: str = Field(default="", description="OAuth callback URL")

    # Embedding Configuration
    # paraphrase-multilingual-MiniLM-L12-v2 : 384 dims (compatible Vector(384) DB),
    # multilingue (50+ langues dont francais et malgache via XLM-RoBERTa base),
    # support stable dans fastembed 0.4+. Pas de prefixe requis (contrairement a E5).
    embedding_model: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        description="FastEmbed model for embeddings (ONNX, no PyTorch). Doit etre 384 dims."
    )

    # RAG Configuration
    rag_top_k: int = Field(default=5, description="Number of documents to retrieve")
    rag_confidence_high: float = Field(default=0.75, description="High confidence threshold")
    rag_confidence_medium: float = Field(default=0.50, description="Medium confidence threshold")
    rag_confidence_low: float = Field(default=0.30, description="Low confidence threshold")

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")

    # Rate Limiting
    rate_limit_requests: int = Field(default=60, description="Max requests per period")
    rate_limit_period: int = Field(default=60, description="Rate limit period in seconds")

    # Support Contact
    support_email: str = Field(default="", description="Support email")
    support_phone: str = Field(default="", description="Support phone")

    # Brevo (emails transactionnels et onboarding)
    brevo_api_key: str = Field(default="", description="Brevo API key (xkeysib-...)")
    mail_from: str = Field(default="contact@valina-bot.com", description="Sender email")
    mail_from_name: str = Field(default="Valina-Bot", description="Sender name displayed in inbox")
    dashboard_base_url: str = Field(default="https://agent.valina-bot.com", description="Dashboard URL for email links")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Retourne l'instance de configuration (cached)"""
    return Settings()


# Instance globale
settings = get_settings()
