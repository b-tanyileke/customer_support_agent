import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNKS_PATH, CHUNK_OVERLAP, CHUNK_SIZE, RAW_DOCS_DIR
from ingest.document_loader import clean_text, read_text_file


splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)

all_chunks = []

for file in sorted(RAW_DOCS_DIR.glob("*.txt")):
    text = clean_text(read_text_file(file))
    chunks = splitter.split_text(text)

    for chunk_id, chunk in enumerate(chunks):
        all_chunks.append(
            {
                "id": f"{file.stem}-{chunk_id:03d}",
                "text": chunk,
                "source": file.name,
                "document": file.stem.replace("_", " ").title(),
                "chunk_id": chunk_id,
            }
        )

CHUNKS_PATH.write_text(json.dumps(all_chunks, indent=2), encoding="utf-8")

print(f"Created {len(all_chunks)} chunks from documents.")
