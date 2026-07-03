"""
Application settings for the support agent.

Values can be overridden with environment variables or a local .env file.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default

    try:
        return float(value)
    except ValueError:
        return default


load_dotenv(BASE_DIR / ".env")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "gemma3:latest")
LLM_TEMPERATURE = _get_float("LLM_TEMPERATURE", 0.2)
LLM_MAX_TOKENS = _get_int("LLM_MAX_TOKENS", 512)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_BASE_URL = os.getenv(
    "GEMINI_BASE_URL",
    "https://generativelanguage.googleapis.com/v1beta",
)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
RETRIEVAL_TOP_K = _get_int("RETRIEVAL_TOP_K", 3)
RETRIEVAL_MIN_SCORE = _get_float("RETRIEVAL_MIN_SCORE", -1.0)
CHUNK_SIZE = _get_int("CHUNK_SIZE", 800)
CHUNK_OVERLAP = _get_int("CHUNK_OVERLAP", 80)

DATA_DIR = BASE_DIR / "data"
METADATA_PATH = DATA_DIR / "metadata.json"
INDEX_PATH = DATA_DIR / "support_index.faiss"
CHUNKS_PATH = DATA_DIR / "chunks.json"
RAW_DOCS_DIR = DATA_DIR / "raw_docs"

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
