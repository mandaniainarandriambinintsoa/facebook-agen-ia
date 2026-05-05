"""
Endpoint /api/tenants/{tenant_id}/test-bot

Permet a un client de tester son bot sans passer par les webhooks Meta.
Utilise pour le futur setup wizard et pour le debug en cours d'usage.

Mode "dry run" : execute le pipeline RAG complet (retriever + generator +
confidence + prospect detection) MAIS n'envoie rien via l'API Meta. La
reponse simulee est retournee directement au client dashboard.
"""

import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from loguru import logger

from app.db.database import get_db
from app.db import crud
from app.db.models import Tenant
from app.auth.dependencies import get_current_tenant
from app.config import settings


router = APIRouter(prefix="/api/tenants", tags=["TestBot"])


# ─── Schemas ─────────────────────────────────────────────────


class TestBotRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="Le message du client simule")
    channel: str = Field(default="messenger", description="messenger | whatsapp | instagram")
    sender_name: str = Field(default="Test User", max_length=100)
    use_chat_history: bool = Field(default=False, description="Si true, charge l historique du test_user")


class RetrievedDoc(BaseModel):
    content: str
    score: float
    metadata: dict


class TestBotResponse(BaseModel):
    response_text: str
    confidence_level: str
    confidence_score: float
    retrieved_docs: list[RetrievedDoc]
    image_url: Optional[str]
    image_would_be_sent: bool
    prospect_detected: bool
    prospect_keyword: Optional[str]
    prospect_category: Optional[str]
    elapsed_ms: int
    model_used: str
    test_sender_id: str


# ─── Endpoint ────────────────────────────────────────────────


@router.post("/{tenant_id}/test-bot", response_model=TestBotResponse)
async def test_bot(
    tenant_id: str,
    payload: TestBotRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
) -> TestBotResponse:
    """Simule un message client et retourne ce que le bot repondrait, sans envoi reel.

    Usage frontend :
    - Setup wizard : "Tester un message avant d activer le bot"
    - Dashboard debug : "Voir comment le bot reagit a une question donnee"

    Le mock sender_id est `test_user_{tenant_id}` pour pouvoir filtrer ces
    interactions des stats prod si besoin (queries SQL avec WHERE sender_id
    NOT LIKE 'test_user_%').
    """
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    if payload.channel not in ("messenger", "whatsapp", "instagram"):
        raise HTTPException(
            status_code=400,
            detail="channel invalide, attendu : messenger | whatsapp | instagram",
        )

    test_sender_id = f"test_user_{tenant.id}"
    started = time.perf_counter()

    # Charge la config du tenant pour custom_system_prompt + conversation_mode
    tenant_config = await crud.get_tenant_config(db, tenant.id)

    # Charge l historique si demande (pour tester resolution references implicites)
    chat_history: list[dict] = []
    if payload.use_chat_history:
        try:
            recent = await crud.get_messages_by_sender(db, tenant.id, test_sender_id, limit=4)
            for log in reversed(recent):
                chat_history.append({"role": "user", "content": log.message_text or ""})
                chat_history.append({"role": "assistant", "content": log.response_text or ""})
        except Exception as e:
            logger.warning(f"test-bot: impossible de charger l historique: {e}")

    # Pipeline RAG (sans envoyer via l API Meta)
    from app.rag.pg_retriever import PgVectorRetriever
    from app.rag.generator import ResponseGenerator
    from app.rag.confidence import ConfidenceHandler

    retriever = PgVectorRetriever(tenant_id=tenant.id, db=db)
    generator = ResponseGenerator(
        custom_system_prompt=(tenant_config.custom_system_prompt if tenant_config else None),
        conversation_mode=(getattr(tenant_config, "conversation_mode", "catalog") if tenant_config else "catalog"),
    )
    confidence_handler = ConfidenceHandler()

    try:
        rag_response = await confidence_handler.process_query_async(
            payload.message, retriever, generator, chat_history=chat_history,
        )
    except Exception as e:
        logger.error(f"test-bot: pipeline RAG en erreur: {e}")
        raise HTTPException(status_code=503, detail=f"LLM indisponible: {str(e)[:200]}")

    # Extraction image_url du top doc si presente
    top_image_url: Optional[str] = None
    if rag_response.top_document and rag_response.top_document.metadata:
        url = rag_response.top_document.metadata.get("image_url")
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            top_image_url = url

    # Decide si l image serait envoyee en prod (memes regles que platforms/base.py)
    from app.platforms.base import _is_image_requested
    image_requested = _is_image_requested(payload.message)
    confidence_level = rag_response.confidence_level.value
    image_would_be_sent = bool(top_image_url) and (
        confidence_level == "high" or image_requested
    )

    # Detection prospect (sans creation en DB)
    prospect_detected = False
    prospect_keyword: Optional[str] = None
    prospect_category: Optional[str] = None
    try:
        from app.rag.prospect_detector import detect_prospect_intent
        intent = detect_prospect_intent(payload.message)
        if intent:
            prospect_detected = True
            prospect_keyword = intent.get("keyword")
            prospect_category = intent.get("category")
    except Exception as e:
        logger.warning(f"test-bot: detection prospect failed: {e}")

    # Log du message test (utile pour debug + use_chat_history sur prochains tests)
    try:
        await crud.log_message(
            db=db,
            tenant_id=tenant.id,
            sender_id=test_sender_id,
            message_text=payload.message,
            response_text=rag_response.response,
            confidence_level=confidence_level,
            confidence_score=rag_response.confidence_score,
            channel=payload.channel,
        )
    except Exception as e:
        logger.warning(f"test-bot: log_message failed (non-bloquant): {e}")

    # Format docs retrieves pour debug frontend
    retrieved_docs: list[RetrievedDoc] = []
    if rag_response.top_document:
        retrieved_docs.append(RetrievedDoc(
            content=(rag_response.top_document.content or "")[:500],
            score=float(rag_response.confidence_score),
            metadata=dict(rag_response.top_document.metadata or {}),
        ))

    elapsed_ms = int((time.perf_counter() - started) * 1000)

    return TestBotResponse(
        response_text=rag_response.response,
        confidence_level=confidence_level,
        confidence_score=float(rag_response.confidence_score),
        retrieved_docs=retrieved_docs,
        image_url=top_image_url,
        image_would_be_sent=image_would_be_sent,
        prospect_detected=prospect_detected,
        prospect_keyword=prospect_keyword,
        prospect_category=prospect_category,
        elapsed_ms=elapsed_ms,
        model_used=settings.llm_model or "unknown",
        test_sender_id=test_sender_id,
    )


# ─── Endpoint reset historique test (utile pour repartir clean) ──


@router.delete("/{tenant_id}/test-bot/history")
async def reset_test_history(
    tenant_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Supprime l historique des tests pour ce tenant.

    Utile si le client veut repartir d'un etat propre dans le wizard ou apres
    avoir teste plusieurs scenarios.
    """
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    test_sender_id = f"test_user_{tenant.id}"
    try:
        from sqlalchemy import delete
        from app.db.models import MessageLog
        result = await db.execute(
            delete(MessageLog).where(
                MessageLog.tenant_id == tenant.id,
                MessageLog.sender_id == test_sender_id,
            )
        )
        await db.commit()
        return {"status": "deleted", "rows_deleted": result.rowcount or 0}
    except Exception as e:
        await db.rollback()
        logger.error(f"test-bot: reset history failed: {e}")
        raise HTTPException(status_code=500, detail="Reset failed")
