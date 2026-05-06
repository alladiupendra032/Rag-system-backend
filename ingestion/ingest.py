from __future__ import annotations

import argparse
import hashlib
import logging
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader
from pinecone import Pinecone, ServerlessSpec

from app.config import get_settings
from app.services.embedding import EmbeddingService

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def load_text_from_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def clean_text(text: str) -> str:
    return " ".join(text.split())


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Pure-Python word-based chunker (no C-extensions, safe for Vercel serverless)."""
    words = text.split()
    if not words:
        return []
    step = max(1, chunk_size - overlap)
    chunks: list[str] = []
    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk.strip())
    return chunks


def iter_docs(source_dir: Path) -> Iterable[Path]:
    for p in sorted(source_dir.rglob("*")):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield p


def ensure_index(pc: Pinecone) -> None:
    settings = get_settings()
    indexes = pc.list_indexes()
    existing = set()
    if hasattr(indexes, "names"):
        existing = set(indexes.names())
    else:
        for idx in indexes:
            name = idx.get("name") if isinstance(idx, dict) else getattr(idx, "name", None)
            if name:
                existing.add(name)
    if settings.pinecone_index_name in existing:
        return
    pc.create_index(
        name=settings.pinecone_index_name,
        dimension=settings.pinecone_index_dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud=settings.pinecone_cloud, region=settings.pinecone_region),
    )
    logger.info("Created Pinecone index: %s", settings.pinecone_index_name)


def build_vector_id(file_name: str, chunk_num: int, text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return f"{file_name}-{chunk_num}-{digest}"


def run_ingestion(source_dir: Path) -> None:
    settings = get_settings()
    pc = Pinecone(api_key=settings.pinecone_api_key)
    ensure_index(pc)

    index = pc.Index(settings.pinecone_index_name)
    embedder = EmbeddingService()
    total_chunks = 0

    for doc_path in iter_docs(source_dir):
        raw = load_text_from_file(doc_path)
        cleaned = clean_text(raw)
        if not cleaned:
            logger.warning("Skipping empty file: %s", doc_path.name)
            continue

        chunks = chunk_text(cleaned, settings.chunk_size_tokens, settings.chunk_overlap_tokens)
        if not chunks:
            logger.warning("No chunks generated for: %s", doc_path.name)
            continue

        embeddings = embedder.embed(chunks)
        vectors = []
        for i, (chunk, vector) in enumerate(zip(chunks, embeddings), start=1):
            vectors.append(
                {
                    "id": build_vector_id(doc_path.name, i, chunk),
                    "values": vector,
                    "metadata": {
                        "text": chunk,
                        "source": doc_path.name,
                        "chunk_id": f"chunk_{i}",
                    },
                }
            )

        index.upsert(vectors=vectors, namespace=settings.pinecone_namespace)
        total_chunks += len(vectors)
        logger.info("Indexed %d chunks from %s", len(vectors), doc_path.name)

    logger.info("Ingestion complete. Total chunks indexed: %d", total_chunks)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="One-time RAG document ingestion")
    parser.add_argument(
        "--source-dir",
        default="rag_docs",
        help="Directory containing PDFs/TXT/MD files",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_ingestion(Path(args.source_dir))
