import time
from dataclasses import dataclass

from pinecone import Pinecone

from app.config import get_settings
from app.services.embedding import EmbeddingService


@dataclass
class RetrievedChunk:
    text: str
    source: str
    chunk_id: str
    score: float


def _retry_call(fn, max_retries: int):
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception:
            if attempt >= max_retries:
                raise
            time.sleep(0.5 * (attempt + 1))


class RetrievalService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.embedding_service = EmbeddingService()
        self.pinecone_client = Pinecone(api_key=self.settings.pinecone_api_key)
        self.index = self.pinecone_client.Index(self.settings.pinecone_index_name)

    def retrieve(self, query: str) -> list[RetrievedChunk]:
        query_vector = self.embedding_service.embed_query(query)

        def _call():
            return self.index.query(
                vector=query_vector,
                top_k=self.settings.retrieval_top_k,
                include_metadata=True,
                namespace=self.settings.pinecone_namespace,
            )

        query_result = _retry_call(_call, self.settings.max_retries)
        matches = getattr(query_result, "matches", []) or []

        chunks: list[RetrievedChunk] = []
        for m in matches:
            metadata = getattr(m, "metadata", None) or {}
            score = getattr(m, "score", 0.0) or 0.0
            text = metadata.get("text", "")
            if not text:
                continue
            chunks.append(
                RetrievedChunk(
                    text=text,
                    source=metadata.get("source", "unknown"),
                    chunk_id=metadata.get("chunk_id", getattr(m, "id", "unknown")),
                    score=score,
                )
            )

        if not chunks:
            return []

        threshold = self.settings.min_relevance_score
        filtered = [c for c in chunks if c.score >= threshold]
        # Avoid false "I don't know" when index scores are naturally low.
        return filtered if filtered else chunks
