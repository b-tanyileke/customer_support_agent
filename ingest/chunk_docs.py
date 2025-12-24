"""
Reads raw text documents, splits them into smaller overlapping chunks,
and saves them for embedding.
"""

# Import necessary libraries
from pathlib import Path
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Set path to raw documents
BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "data/raw_docs"
OUTPUT_DIR = BASE_DIR / "data/chunks.json"

# Text splitter configuration
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=50)

all_chunks = []

# Iterate over raw documents
for file in DOCS_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")

    # Split text into chunks
    chunks = splitter.split_text(text)
    # store chunks
    for chunk in chunks:
        all_chunks.append({"text": chunk, "source": file.name})

# Save chunks to disk
OUTPUT_DIR.write_text(json.dumps(all_chunks, indent=2))

# Debug message
print(f"Created {len(all_chunks)} chunks from documents.")
