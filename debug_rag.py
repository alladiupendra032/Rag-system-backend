import sys
sys.path.insert(0, ".")

from app.config import get_settings
from app.services.embedding import EmbeddingService
from pinecone import Pinecone

s = get_settings()
pc = Pinecone(api_key=s.pinecone_api_key)
index = pc.Index(s.pinecone_index_name)

print("=== INDEX STATS ===")
stats = index.describe_index_stats()
print("Total vectors:", stats.total_vector_count)
print("Namespaces:", stats.namespaces)
print()

embedder = EmbeddingService()
query = "What is the return policy?"
print("Query:", query)
vec = embedder.embed_query(query)
print("Vector dim:", len(vec), "  first 4:", vec[:4])
print()

result = index.query(
    vector=vec,
    top_k=5,
    include_metadata=True,
    namespace=s.pinecone_namespace,
)

matches = getattr(result, "matches", []) or []
print("TOP", len(matches), "MATCHES")
for m in matches:
    meta = getattr(m, "metadata", {}) or {}
    score = getattr(m, "score", 0.0)
    text  = meta.get("text", "")
    src   = meta.get("source", "NO_SOURCE")
    cid   = meta.get("chunk_id", "NO_CHUNK_ID")
    has_text = "YES" if text else "NO"
    print("  ID:", m.id)
    print("  Score:", round(score, 4))
    print("  Source:", src)
    print("  ChunkID:", cid)
    print("  Has text in metadata:", has_text)
    if text:
        print("  Text[0:200]:", text[:200])
    print()
