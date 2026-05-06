from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    _ROOT_DIR = Path(__file__).resolve().parent.parent
    model_config = SettingsConfigDict(
        env_file=(
            str(_ROOT_DIR / ".env"),
            ".env",
            "../.env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Website RAG Chatbot API"
    app_env: str = "dev"
    app_api_key: str | None = Field(
        default=None, validation_alias=AliasChoices("APP_API_KEY", "app_api_key")
    )

    pinecone_api_key: str = Field(
        ..., validation_alias=AliasChoices("PINECONE_API_KEY", "pinecone_api_key")
    )
    pinecone_index_name: str = Field(
        default="rag-chatbot-index",
        validation_alias=AliasChoices("PINECONE_INDEX_NAME", "pinecone_index_name"),
    )
    pinecone_index_dimension: int = Field(
        default=1024,
        validation_alias=AliasChoices("PINECONE_INDEX_DIMENSION", "pinecone_index_dimension"),
    )
    pinecone_namespace: str = Field(
        default="default",
        validation_alias=AliasChoices("PINECONE_NAMESPACE", "pinecone_namespace"),
    )
    pinecone_cloud: str = Field(
        default="aws", validation_alias=AliasChoices("PINECONE_CLOUD", "pinecone_cloud")
    )
    pinecone_region: str = Field(
        default="us-east-1",
        validation_alias=AliasChoices("PINECONE_REGION", "pinecone_region"),
    )
    embedding_model: str = Field(
        default="llama-text-embed-v2",
        validation_alias=AliasChoices("EMBEDDING_MODEL", "embedding_model"),
    )

    groq_api_key: str = Field(..., validation_alias=AliasChoices("GROQ_API_KEY", "groq_api_key"))
    llm_model: str = Field(
        default="llama-3.3-70b-versatile",
        validation_alias=AliasChoices("LLM_MODEL", "llm_model"),
    )
    llm_temperature: float = Field(
        default=0.3, validation_alias=AliasChoices("LLM_TEMPERATURE", "llm_temperature")
    )
    llm_max_tokens: int = Field(
        default=500, validation_alias=AliasChoices("LLM_MAX_TOKENS", "llm_max_tokens")
    )

    retrieval_top_k: int = Field(
        default=5, validation_alias=AliasChoices("RETRIEVAL_TOP_K", "retrieval_top_k")
    )
    min_relevance_score: float = Field(
        default=0.6,
        validation_alias=AliasChoices("MIN_RELEVANCE_SCORE", "min_relevance_score"),
    )
    chunk_size_tokens: int = Field(
        default=500, validation_alias=AliasChoices("CHUNK_SIZE_TOKENS", "chunk_size_tokens")
    )
    chunk_overlap_tokens: int = Field(
        default=100,
        validation_alias=AliasChoices("CHUNK_OVERLAP_TOKENS", "chunk_overlap_tokens"),
    )

    request_timeout_seconds: int = Field(
        default=25,
        validation_alias=AliasChoices("REQUEST_TIMEOUT_SECONDS", "request_timeout_seconds"),
    )
    max_retries: int = Field(
        default=2, validation_alias=AliasChoices("MAX_RETRIES", "max_retries")
    )

    rate_limit_per_minute: int = Field(
        default=40,
        validation_alias=AliasChoices("RATE_LIMIT_PER_MINUTE", "rate_limit_per_minute"),
    )
    cors_allow_origins: str = Field(
        default="*",
        validation_alias=AliasChoices("CORS_ALLOW_ORIGINS", "cors_allow_origins"),
    )

    def parsed_cors_origins(self) -> list[str]:
        origins = [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]
        return origins or ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
