# Enterprise AI Support Agent (RAG-Based)

An enterprise-style AI support agent that answers customer support questions using
**retrieval-augmented generation (RAG)**, **LLM-based intent classification**, and
**explicit decision logic**. The system is designed to be safe and modular,
mirroring real-world AI agent workflows used in customer care systems.

---

## Features

- **LLM-based intent classification**
  - Classifies queries into billing, technical support, service terms, production or escalation.
- **Retrieval-Augmented Generation (RAG)**
  - Uses sentence-transformer embeddings and FAISS for semantic search
- **Escalation handling**
  - Automatically defers to a human agent when confidence is low
- **FastAPI backend**
  - Clean API interface for integration
- **Streamlit UI**
  - Simple chat interface for demos and testing
- **Evaluation utilities**
  - Intent accuracy and retrieval sanity checks

---

## Architecture Overview

```text
User Query
   ↓
LLM-Based Intent Classification
   ↓
Vector Retrieval (FAISS)
   ↓
Grounded LLM Response (Gemma)
   ↓
Escalation if needed
```

---

## Project Structure
```test
ai_support_agent/
│
├── data/
│   ├── raw_docs/              # Fictional enterprise support documents
│   ├── chunks.json            # Chunked documents
│   ├── metadata.json          # Chunk metadata
│   └── support_index.faiss    # FAISS vector index
│
├── ingest/
│   ├── chunk_docs.py          # Document chunking
│   └── embed_store.py         # Embedding + vector store creation
│
├── agent/
│   ├── intent_classifier.py   # Intent classifier
│   ├── retriever.py           # Relevant chunk retriever
│   ├── prompts.py             # Prompts for LLM
│   └── support_agent.py       # Query handling
│
├── api/
│   └── app.py                 # FastAPI backend
│
├── ui/
│   └── streamlit_app.py       # Streamlit UI
│
├── eval/
│   └── evaluate.py            # Evaluation scripts
│
├── requirements.txt
└── README.md
```
---

## Setup Instructions

1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Install and start Ollama
```bash
ollama pull gemma
```

---

## Data Preparation

All documents are fictional and created solely for demonstration.
```bash
python ingest/chunk_docs.py
python ingest/embed_store.py
```

---

## Running the Application

1. Start the API
```bash
uvicorn api.app:app --reload
```

2. Launch the UI
```bash
streamlit run ui/streamlit_app.py
```

---

## Evaluation

Run basic evaluation checks:
```bash
python eval/evaluate.py
```

---

## Possible Future Enhancements

- Query rewriting for improved retrieval

-  Confidence scoring for responses

- LLM-based evaluation

- Dockerized deployment

- Persistent conversation memory
