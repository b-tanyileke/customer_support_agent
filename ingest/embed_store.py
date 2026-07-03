"""
Store embeddings for the support documents in a FAISS index.
"""

import json
from pathlib import Path
import sys
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from config import CHUNKS_PATH, EMBEDDING_MODEL, INDEX_PATH, METADATA_PATH


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
texts = [chunk["text"] for chunk in chunks]

if not texts:
    raise ValueError("No chunks found. Run python ingest/chunk_docs.py first.")

model = SentenceTransformer(EMBEDDING_MODEL)
embeddings = model.encode(
    texts,
    show_progress_bar=True,
    normalize_embeddings=True,
)
embeddings = np.asarray(embeddings, dtype="float32")

dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

faiss.write_index(index, str(INDEX_PATH))
METADATA_PATH.write_text(json.dumps(chunks, indent=2), encoding="utf-8")

print(f"Stored {len(texts)} normalized embeddings in FAISS index.")
