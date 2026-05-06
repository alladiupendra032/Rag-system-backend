from __future__ import annotations

import time
from typing import Any

from pinecone import Pinecone

from app.config import get_settings


def _retry_call(fn, max_retries: int):
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception:
            if attempt >= max_retries:
                raise
            time.sleep(0.5 * (attempt + 1))


class EmbeddingService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = Pinecone(api_key=self.settings.pinecone_api_key)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        parameters: dict[str, Any] = {"input_type": "passage", "truncate": "END"}
        model_name = self.settings.embedding_model

        def _call():
            return self.client.inference.embed(
                model=model_name,
                inputs=texts,
                parameters=parameters,
            )

        result = _retry_call(_call, self.settings.max_retries)
        vectors: list[list[float]] = []
        for item in result.data:
            values = getattr(item, "values", None)
            if values is None and isinstance(item, dict):
                values = item.get("values")
            if not values:
                raise ValueError("Pinecone embedding response did not include vector values.")
            vectors.append(list(values))
        return vectors

    def embed_query(self, query: str) -> list[float]:
        parameters = {"input_type": "query", "truncate": "END"}
        model_name = self.settings.embedding_model

        def _call():
            return self.client.inference.embed(
                model=model_name,
                inputs=[query],
                parameters=parameters,
            )

        result = _retry_call(_call, self.settings.max_retries)
        item = result.data[0]
        values = getattr(item, "values", None)
        if values is None and isinstance(item, dict):
            values = item.get("values")
        if not values:
            raise ValueError("Pinecone query embedding response did not include vector values.")
        return list(values)
