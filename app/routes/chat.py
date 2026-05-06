from __future__ import annotations

import logging
from time import perf_counter

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.config import get_settings
from app.models import ChatRequest, ChatResponse
from app.services.rag import RAGService
from app.services.rate_limit import rate_limit

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])
rag_service = RAGService()


def verify_optional_api_key(x_api_key: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if settings.app_api_key and x_api_key != settings.app_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key.")


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    request: Request,
    _api_key_ok: None = Depends(verify_optional_api_key),
) -> ChatResponse:
    if not payload.query.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query cannot be empty.")

    rate_limit(request)
    start = perf_counter()

    try:
        response = rag_service.answer_query(payload.query.strip())
        total_ms = (perf_counter() - start) * 1000
        logger.info("chat_request_success latency_ms=%.2f", total_ms)
        return response
    except HTTPException:
        raise
    except TimeoutError:
        logger.exception("chat_request_timeout")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Upstream model timeout. Please try again.",
        )
    except Exception:
        logger.exception("chat_request_failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate response. Please retry.",
        )
