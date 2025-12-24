"""
Creates embeddings for document chunks and stores them in a FAISS index.
"""

# Import necessary libraries
from pathlib import Path
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


# Load chunked documents
BASE_DIR = Path(__file__).resolve().parent.parent
METADATA_PATH = BASE_DIR / "data/metadata.json" # to save metadata
CHUNK_PATH = BASE_DIR / "data/chunks.json"
chunks = json.loads(CHUNK_PATH.read_text())
texts = [chunk["text"] for chunk in chunks]


# Load sentence transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")
# generate embeddings
embeddings = model.encode(texts, show_progress_bar=True)

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# Save FAISS index and metadata
faiss.write_index(index, str(BASE_DIR / "data/support_index.faiss"))
METADATA_PATH.write_text(json.dumps(chunks, indent=2))

print(f"Stored {len(texts)} embeddings in FAISS index.")
