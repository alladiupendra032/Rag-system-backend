# Rag-system-backend

Production-ready FastAPI backend for a strict RAG chatbot.

It reads documents from `rag_docs`, uploads chunk embeddings to Pinecone, and answers user queries by:
1) retrieving top related chunks from vector DB, then
2) generating a grounded answer from those chunks using LLM.

If context is not available, the API returns `"I don't know."`.

---

## 1. What This Project Contains

### Core capabilities
- One-time (or manual repeat) document ingestion from local folder.
- Token-based chunking (`chunk_size=500`, `overlap=100`).
- Embedding generation with Pinecone embedding model (`EMBEDDING_MODEL`).
- Vector retrieval from Pinecone index (`PINECONE_INDEX_NAME` + namespace).
- LLM answer generation through Groq model (`LLM_MODEL`).
- FastAPI endpoint for chatbot response.
- Optional API key protection and in-memory rate limiting.
- Basic logging for request status, latency, and token usage.

### Current operation mode
- Strict RAG mode:
  - Uses retrieved document context only.
  - No chat memory/history.
  - No fallback to external knowledge.

---

## 2. Project Structure

```text
app/
  main.py                  # FastAPI app bootstrap + health route
  config.py                # Environment/settings loader
  models.py                # Request/response schema
  routes/
    chat.py                # /chat endpoint
  services/
    embedding.py           # Pinecone embedding calls
    retrieval.py           # Vector search
    prompt.py              # Prompt template
    llm.py                 # Groq generation (stream enabled internally)
    rag.py                 # End-to-end RAG orchestration
    rate_limit.py          # In-memory per-IP limiter
ingestion/
  ingest.py                # Document loader/chunker/index upsert
rag_docs/                  # Source documents (PDF/TXT/MD)
requirements.txt
.env.example
README.md
```

---

## 3. Environment Configuration

Create `.env` in project root.

### Required keys
- `PINECONE_API_KEY`
- `GROQ_API_KEY`

### Recommended keys
- `PINECONE_INDEX_NAME=rag`
- `PINECONE_INDEX_DIMENSION=1024`
- `PINECONE_NAMESPACE=default`
- `PINECONE_CLOUD=aws`
- `PINECONE_REGION=us-east-1`
- `EMBEDDING_MODEL=llama-text-embed-v2`
- `LLM_MODEL=llama-3.3-70b-versatile`
- `RATE_LIMIT_PER_MINUTE=40`
- `APP_API_KEY=` (optional, keep blank to disable API-key auth)

---

## 4. Installation

From project root:

```powershell
python -m pip install -r requirements.txt
```

---

## 5. Ingestion (Upload Docs to Pinecone)

### Source folder
- Default source folder is `rag_docs`.
- Supported file types: `.pdf`, `.txt`, `.md`.

### Run ingestion

```powershell
python -m ingestion.ingest --source-dir rag_docs
```

### Force upload into a specific index (example: `rag`)

```powershell
$env:PINECONE_INDEX_NAME='rag'; python -m ingestion.ingest --source-dir rag_docs
```

### Fresh re-upload (clear namespace then upload again)

```powershell
$env:PINECONE_INDEX_NAME='rag'; python -c "from app.config import get_settings; from pinecone import Pinecone; s=get_settings(); Pinecone(api_key=s.pinecone_api_key).Index(s.pinecone_index_name).delete(delete_all=True, namespace=s.pinecone_namespace); print('cleared')"
$env:PINECONE_INDEX_NAME='rag'; python -m ingestion.ingest --source-dir rag_docs
```

---

## 6. Run FastAPI Server

Recommended command (works even if terminal path changes):

```powershell
python -m uvicorn app.main:app --reload --app-dir "C:\Users\allad\OneDrive\Desktop\Rag Backend" --port 8001
```

Open docs:
- Swagger UI: `http://127.0.0.1:8001/docs`
- Health: `http://127.0.0.1:8001/health`

---

## 7. API Endpoints

## `GET /health`

Health check endpoint.

### Response
```json
{
  "status": "ok"
}
```

---

## `POST /chat`

Main chatbot endpoint.

### Request body
```json
{
  "query": "What is your return policy?"
}
```

### Headers
- `Content-Type: application/json`
- Optional if `APP_API_KEY` is set:
  - `x-api-key: <your-api-key>`

### Success response
```json
{
  "answer": "Our return policy allows ...",
  "sources": [
    {
      "file": "return_policy.pdf",
      "chunk_id": "chunk_1"
    }
  ]
}
```

### Error behavior
- `400` for empty query
- `401` if API key is required and invalid/missing
- `429` rate limit exceeded
- `500` upstream/internal failure
- `504` model timeout

---

## 8. How Query Processing Works

For each `/chat` request:
1. Validate non-empty `query`.
2. Optional API key check.
3. Rate-limit check (in-memory, per IP, 60-second window).
4. Convert query text to embedding vector.
5. Run Pinecone vector similarity search (`top_k` from config).
6. Build strict prompt from retrieved chunks.
7. Call Groq chat model (streaming enabled internally and aggregated).
8. Return final JSON with `answer` + `sources`.

---

## 9. Integration Guide For Another Website

Use this endpoint from frontend/backend:

- URL: `http://127.0.0.1:8001/chat`
- Method: `POST`
- Body: `{ "query": "..." }`
- Header: `x-api-key` only if enabled

### JavaScript fetch example

```javascript
async function askBot(userMessage) {
  const res = await fetch("http://127.0.0.1:8001/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      // "x-api-key": "your_api_key_here" // if APP_API_KEY is set
    },
    body: JSON.stringify({ query: userMessage })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Chat request failed");
  }

  return res.json(); // { answer, sources }
}
```

### Typical frontend usage
- Send user message to `/chat`.
- Render `answer` in chat bubble.
- Optionally show `sources` as citations.

---

## 10. Notes and Troubleshooting

- If you see `No module named 'app'`:
  - run from project root, or use `--app-dir`.

- If you see missing env errors (`PINECONE_API_KEY`, `GROQ_API_KEY`):
  - verify `.env` exists in project root and keys are correct.

- If response is `"I don't know."`:
  - verify index has records in the same namespace,
  - ensure docs are ingested into the same `PINECONE_INDEX_NAME`,
  - check query relevance against uploaded docs.

- If port already in use:
  - run with another port (e.g. `--port 8001`).

---

## 11. Security and Production Notes

- Current rate limiting is in-memory and single-instance only.
- Use reverse proxy/API gateway for production-grade throttling and auth.
- Keep API keys in env only, never hardcode.
- For deployment, configure CORS explicitly for your website domain.

---

## 12. Current Limitations

- No conversation memory.
- No hybrid search (keyword + vector).
- No caching.
- No SSE streaming response to clients yet (internal provider streaming is enabled).

---

## 13. Quick Start (Minimal)

```powershell
python -m pip install -r requirements.txt
python -m ingestion.ingest --source-dir rag_docs
python -m uvicorn app.main:app --reload --app-dir "C:\Users\allad\OneDrive\Desktop\Rag Backend" --port 8001
```
