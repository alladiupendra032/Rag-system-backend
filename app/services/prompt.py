def build_rag_prompt(retrieved_chunks: str, user_query: str) -> str:
    return f"""You are a helpful AI assistant.

Use ONLY the context below to answer the question.
If the answer is not found, say "I don't know."

Context:
{retrieved_chunks}

Question:
{user_query}

Answer:
"""
