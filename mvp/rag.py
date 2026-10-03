"""
Lightweight in-memory RAG — no Chroma, no C++ dependencies.
Uses simple TF-IDF-style keyword search over lease text chunks.
Keeps the same build_vectorstore / query_portfolio interface.
"""

import re
from typing import Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def _score(chunk: str, query: str) -> float:
    """Simple keyword overlap score (case-insensitive)."""
    query_words = set(re.findall(r"\w+", query.lower()))
    chunk_words = re.findall(r"\w+", chunk.lower())
    if not chunk_words:
        return 0.0
    matches = sum(1 for w in chunk_words if w in query_words)
    return matches / len(chunk_words)


def build_vectorstore(lease_texts: dict[str, str]) -> dict[str, Any]:
    """
    Build an in-memory 'vectorstore' (just chunked text + metadata).
    lease_texts: {filename: full_text}
    Returns a dict that query_portfolio understands.
    """
    chunks = []
    for filename, text in lease_texts.items():
        for chunk in _chunk_text(text):
            chunks.append({"filename": filename, "text": chunk})
    return {"chunks": chunks}


def query_portfolio(vectorstore: dict[str, Any], question: str) -> dict[str, Any]:
    """
    Find the most relevant chunks and ask GPT-4o to answer the question.
    Returns {"answer": str, "sources": list[str]}.
    """
    chunks = vectorstore.get("chunks", [])
    if not chunks:
        return {"answer": "No leases indexed yet.", "sources": []}

    # rank chunks by keyword overlap
    scored = sorted(chunks, key=lambda c: _score(c["text"], question), reverse=True)
    top = scored[:5]

    context_parts = []
    for c in top:
        context_parts.append(f"[{c['filename']}]\n{c['text']}")
    context = "\n\n---\n\n".join(context_parts)

    prompt = (
        f"You are a Portuguese commercial real estate analyst.\n"
        f"Answer the question using only the lease excerpts below.\n"
        f"Be specific and cite the lease filename when relevant.\n\n"
        f"Question: {question}\n\n"
        f"Lease excerpts:\n{context}"
    )

    response = _get_client().chat.completions.create(
        model="gpt-4o-2024-11-20",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.1,
    )

    sources = list({c["filename"] for c in top})
    return {
        "answer": response.choices[0].message.content,
        "sources": sources,
    }
