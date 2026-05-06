import hashlib
import logging
import shutil
import tempfile
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pinecone import Pinecone as _Pinecone

from app.config import get_settings
from app.services.embedding import EmbeddingService
from ingestion.ingest import chunk_text, clean_text, load_text_from_file

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ingest"])

SUPPORTED = {".md", ".txt", ".pdf"}


# ── Lazy singletons — initialized on first request, not at import time ────────
@lru_cache(maxsize=1)
def _get_index():
    s = get_settings()
    pc = _Pinecone(api_key=s.pinecone_api_key)
    return pc.Index(s.pinecone_index_name)


@lru_cache(maxsize=1)
def _get_embedder() -> EmbeddingService:
    return EmbeddingService()


def verify_optional_api_key(x_api_key: str | None = Header(default=None)) -> None:
    s = get_settings()
    if s.app_api_key and x_api_key != s.app_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key.")


def _build_vector_id(filename: str, chunk_num: int, text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return f"{filename}-{chunk_num}-{digest}"


def _delete_file_vectors(filename: str) -> int:
    """Delete all Pinecone vectors whose 'source' metadata matches filename."""
    s = get_settings()
    index = _get_index()
    try:
        result = index.query(
            vector=[0.0] * s.pinecone_index_dimension,
            top_k=10000,
            include_metadata=True,
            namespace=s.pinecone_namespace,
            filter={"source": {"$eq": filename}},
        )
        ids_to_delete = [m.id for m in (result.matches or []) if m.metadata.get("source") == filename]
        if ids_to_delete:
            index.delete(ids=ids_to_delete, namespace=s.pinecone_namespace)
        return len(ids_to_delete)
    except Exception as exc:
        logger.warning("Could not delete old vectors for %s: %s", filename, exc)
        return 0


# ── POST /ingest/upload ───────────────────────────────────────────────────────
@router.post("/ingest/upload")
async def upload_and_ingest(
    file: UploadFile = File(...),
    _api_key_ok: None = Depends(verify_optional_api_key),
) -> JSONResponse:
    s = get_settings()
    suffix = Path(file.filename).suffix.lower()
    if suffix not in SUPPORTED:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {', '.join(SUPPORTED)}",
        )

    # Save to temp file so load_text_from_file can handle PDFs properly
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        raw = load_text_from_file(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    cleaned = clean_text(raw)
    if not cleaned:
        raise HTTPException(status_code=422, detail="File is empty or has no readable text.")

    chunks = chunk_text(cleaned, s.chunk_size_tokens, s.chunk_overlap_tokens)
    if not chunks:
        raise HTTPException(status_code=422, detail="Could not split file into chunks.")

    # Delete old vectors for this filename before re-indexing
    deleted_count = _delete_file_vectors(file.filename)
    logger.info("Deleted %d old vectors for '%s'", deleted_count, file.filename)

    # Embed + upsert
    embeddings = _get_embedder().embed(chunks)
    vectors = []
    for i, (chunk, vector) in enumerate(zip(chunks, embeddings), start=1):
        vectors.append({
            "id":       _build_vector_id(file.filename, i, chunk),
            "values":   vector,
            "metadata": {
                "text":     chunk,
                "source":   file.filename,
                "chunk_id": f"chunk_{i}",
            },
        })

    _get_index().upsert(vectors=vectors, namespace=s.pinecone_namespace)
    logger.info("Ingested %d chunks from '%s' (replaced %d old)", len(vectors), file.filename, deleted_count)

    return JSONResponse({
        "status":        "ok",
        "file":          file.filename,
        "chunks_indexed": len(vectors),
        "old_chunks_removed": deleted_count,
    })


# ── GET /ingest/files ─────────────────────────────────────────────────────────
@router.get("/ingest/files")
def list_indexed_files(
    _api_key_ok: None = Depends(verify_optional_api_key),
) -> JSONResponse:
    """Return a list of distinct source filenames and their chunk counts from Pinecone."""
    s = get_settings()
    index = _get_index()
    try:
        stats = index.describe_index_stats()
        total = stats.total_vector_count or 0

        # Sample up to 10 000 vectors to discover distinct filenames
        dummy_vec = [0.0] * s.pinecone_index_dimension
        result = index.query(
            vector=dummy_vec,
            top_k=min(total, 10000) if total > 0 else 1,
            include_metadata=True,
            namespace=s.pinecone_namespace,
        )
        file_chunks: dict[str, int] = {}
        for m in (result.matches or []):
            src = (m.metadata or {}).get("source", "unknown")
            file_chunks[src] = file_chunks.get(src, 0) + 1

        files = [{"file": k, "chunks": v} for k, v in sorted(file_chunks.items())]
        return JSONResponse({"files": files, "total_vectors": total})
    except Exception as exc:
        logger.exception("list_indexed_files failed")
        raise HTTPException(status_code=500, detail=str(exc))


# ── DELETE /ingest/files/{filename} ──────────────────────────────────────────
@router.delete("/ingest/files/{filename:path}")
def delete_indexed_file(
    filename: str,
    _api_key_ok: None = Depends(verify_optional_api_key),
) -> JSONResponse:
    """Remove all Pinecone vectors for a given source filename."""
    deleted = _delete_file_vectors(filename)
    return JSONResponse({"status": "ok", "file": filename, "chunks_removed": deleted})
