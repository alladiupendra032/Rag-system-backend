import logging
from time import perf_counter

from app.models import ChatResponse, SourceItem
from app.services.llm import LLMService
from app.services.prompt import build_rag_prompt
from app.services.retrieval import RetrievalService

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self) -> None:
        self.retrieval_service = RetrievalService()
        self.llm_service = LLMService()

    def answer_query(self, query: str) -> ChatResponse:
        start = perf_counter()
        chunks = self.retrieval_service.retrieve(query)

        if not chunks:
            latency_ms = (perf_counter() - start) * 1000
            logger.info("query_completed no_context latency_ms=%.2f", latency_ms)
            return ChatResponse(answer="I don't know.", sources=[])

        context = "\n\n".join(
            [f"[{i + 1}] ({c.source}::{c.chunk_id}) {c.text}" for i, c in enumerate(chunks)]
        )
        prompt = build_rag_prompt(context, query)
        answer, usage = self.llm_service.generate_answer(prompt)
        latency_ms = (perf_counter() - start) * 1000

        logger.info(
            "query_completed chunks=%d latency_ms=%.2f usage=%s",
            len(chunks),
            latency_ms,
            usage,
        )

        return ChatResponse(
            answer=answer,
            sources=[SourceItem(file=c.source, chunk_id=c.chunk_id) for c in chunks],
        )
