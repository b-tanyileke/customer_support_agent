"""
Loads the FAISS index and retrieves the most relevant document chunks for a given entry
"""

# Import necessary libraries
import json
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent
METADATA_PATH = BASE_DIR / "data/metadata.json" 
INDEX_PATH = BASE_DIR / "data/support_index.faiss"

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index and metadata
index = faiss.read_index(str(INDEX_PATH))
metadata = json.loads(METADATA_PATH.read_text())

def retrieve(query: str, top_k:int = 3):
    """
    Retrieve top_k most relevant document chunks for a query.
    
    :param query: User question
    :type query: str
    :param top_k: Number of chunks to retrieve
    :type top_k: int
    """

    # Convert query to embedding
    query_embedding = model.encode([query])

    # Perform similarity search
    _, indices = index.search(np.array(query_embedding), top_k)
    # Fetch matching results
    results = [metadata[i]["text"] for i in indices[0]]

    return results
