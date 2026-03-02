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
    llm_provider: Literal["anthropic", "openai", "groq"] = Field(default="openai", description="LLM Provider principal")
    llm_model: str = Field(default="gpt-4o-mini", description="LLM Model")
    groq_model: str = Field(default="llama-3.3-70b-versatile", description="Groq fallback model")

    # n8n Configuration
    n8n_base_url: str = Field(default="", description="n8n instance URL")

    # ChromaDB Configuration
    chroma_persist_directory: str = Field(default="./data/chroma_db", description="ChromaDB storage path")
    chroma_collection_name: str = Field(default="knowledge_base", description="ChromaDB collection name")

    # Embedding Configuration
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Sentence transformer model for embeddings"
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
    support_email: str = Field(default="support@example.com", description="Support email")
    support_phone: str = Field(default="", description="Support phone")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Retourne l'instance de configuration (cached)"""
    return Settings()


# Instance globale
settings = get_settings()
