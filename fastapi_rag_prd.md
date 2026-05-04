# 📄 FastAPI RAG Chatbot Backend PRD

## 1. Product Overview

**Product Name:** Website RAG Chatbot API  
**Type:** Stateless backend service (FastAPI)  
**Users:** General public (high concurrency expected)

### Goal
Provide accurate, context-aware responses from a predefined knowledge base (`rag_doc`) via a REST API.

---

## 2. System Scope

### Included
- Query processing API
- RAG pipeline
- Vector search
- LLM response generation
- One-time document ingestion

### Excluded
- UI / frontend
- Admin dashboard
- Continuous document sync

---

## 3. High-Level Architecture

Client (Website)
   ↓
FastAPI (Vercel)
   ↓
RAG Pipeline
   ├── Embedding (Pinecone model)
   ├── Vector Search (Pinecone DB)
   ├── Context Builder
   ├── LLM (Grok)
   ↓
Response JSON

---

## 4. Core Components

### 4.1 FastAPI Service

#### Endpoint: `/chat`

**Method:** POST  

**Request:**
{
  "query": "What is your return policy?"
}

**Response:**
{
  "answer": "Our return policy allows...",
  "sources": [
    {
      "file": "policy.pdf",
      "chunk_id": "chunk_12"
    }
  ]
}

---

### 4.2 Document Ingestion (One-Time Sync)

#### Source
- `rag_doc/` folder

#### Supported Formats
- PDF
- TXT
- Markdown

---

### Pipeline

1. Load documents  
2. Clean text  
3. Chunk text  

#### Chunking Strategy
- Chunk size: **500 tokens**
- Overlap: **100 tokens**

---

### 4.3 Embedding Layer

- Model: `llama-text-embed-v2`
- Provider: Pinecone

#### Process
- Convert chunks → vectors  
- Store in Pinecone index  

---

### 4.4 Pinecone Vector DB Design

{
  "id": "unique_chunk_id",
  "values": [embedding_vector],
  "metadata": {
    "text": "chunk content",
    "source": "file_name",
    "chunk_id": "chunk_number"
  }
}

---

### 4.5 Retrieval Layer

- Query → embedding  
- Perform similarity search  

#### Config
- Top-K: **5**
- Metric: cosine similarity  

---

### 4.6 Prompt Engineering

You are a helpful AI assistant.

Use ONLY the context below to answer the question.
If the answer is not found, say "I don't know."

Context:
{retrieved_chunks}

Question:
{user_query}

Answer:

---

### 4.7 LLM Layer

- Model: `llama-3.3-70b-versatile`
- Provider: Grok  

#### Parameters
- Temperature: 0.3  
- Max tokens: 500  

---

### 4.8 Response Builder

- Extract answer  
- Attach metadata (sources)  
- Return JSON  

---

## 5. Functional Behavior

### Normal Flow

1. Receive query  
2. Generate embedding  
3. Retrieve Top-5 chunks  
4. Build prompt  
5. Call LLM  
6. Return response  

---

### Edge Cases

| Case | Behavior |
|------|--------|
| No relevant docs | Return "I don't know" |
| Empty query | 400 error |
| API failure | Retry (max 2 times) |
| Timeout | Return fallback error |

---

## 6. Non-Functional Requirements

### Performance
- Target latency: **2–4 seconds**

### Scalability
- Stateless API
- Supports concurrent users

### Reliability
- Retry:
  - Pinecone → 2 retries  
  - Grok → 2 retries  

### Security
- Optional API key middleware  
- Rate limiting  

---

## 7. Deployment (Vercel)

### Notes
- Serverless environment  
- Possible cold starts  
- Execution time limits  

### Setup
- FastAPI via ASGI adapter  
- Deploy as serverless function  

---

## 8. Logging & Monitoring

- Request logs  
- Error logs  
- Latency tracking  
- Token usage tracking  

---

## 9. Folder Structure

project/
│
├── app/
│   ├── main.py
│   ├── routes/
│   │   └── chat.py
│   ├── services/
│   │   ├── embedding.py
│   │   ├── retrieval.py
│   │   ├── llm.py
│   │   └── prompt.py
│   ├── utils/
│   └── config.py
│
├── ingestion/
│   └── ingest.py
│
├── rag_doc/
│
└── requirements.txt

---

## 10. Risks & Constraints

### Vercel Limits
- Execution timeout risk for LLM calls  

### Cost Scaling
- Pinecone + LLM cost increases with traffic  

### No Caching
- Repeated queries increase cost  

---

## 11. Future Enhancements

- Chat history (memory)  
- Streaming responses  
- Query caching  
- Hybrid search  
- Admin upload panel  

---

## 12. Mode of Operation

**Current Mode:** Strict RAG  

- Only answers from documents  
- If not found → "I don't know"  

---

## ✅ Summary

This system delivers a scalable, production-ready RAG chatbot backend using:

- FastAPI
- Pinecone vector database
- Grok LLM
- Serverless deployment (Vercel)
