"""
Retrieval module that handles vector search for relevant document chunks.
This module loads the FAISS index and metadata, and provides a function to retrieve
the top-k relevant chunks for a given query.
"""

import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from config import (
    EMBEDDING_MODEL,
    INDEX_PATH,
    METADATA_PATH,
    RETRIEVAL_MIN_SCORE,
    RETRIEVAL_TOP_K,
)


class RetrievalError(RuntimeError):
    """Raised when the vector index or metadata cannot be loaded."""


_model = None
_index = None
_metadata = None


def _load_metadata(path: Path):
    if not path.exists():
        raise RetrievalError(
            f"Missing metadata file at {path}. Run python ingest/chunk_docs.py "
            "and python ingest/embed_store.py first."
        )

    return json.loads(path.read_text(encoding="utf-8"))


def _get_resources():
    global _model, _index, _metadata

    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)

    if _index is None:
        if not INDEX_PATH.exists():
            raise RetrievalError(
                f"Missing FAISS index at {INDEX_PATH}. "
                "Run python ingest/embed_store.py first."
            )
        _index = faiss.read_index(str(INDEX_PATH))

    if _metadata is None:
        _metadata = _load_metadata(METADATA_PATH)

    return _model, _index, _metadata


def retrieve(query: str, top_k: int = RETRIEVAL_TOP_K):
    """
    Retrieve top_k relevant chunks with source and distance metadata.
    """
    if not query.strip():
        return []

    model, index, metadata = _get_resources()
    query_embedding = model.encode([query], normalize_embeddings=True)
    query_embedding = np.asarray(query_embedding, dtype="float32")
    scores, indices = index.search(query_embedding, top_k)

    results = []
    for score, index_id in zip(scores[0], indices[0]):
        if index_id < 0 or index_id >= len(metadata):
            continue
        if score < RETRIEVAL_MIN_SCORE:
            continue

        item = metadata[index_id]
        results.append(
            {
                "text": item["text"],
                "source": item.get("source", "unknown"),
                "document": item.get("document", "Unknown"),
                "chunk_id": item.get("chunk_id"),
                "score": float(score),
            }
        )

    return results
