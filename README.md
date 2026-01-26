# Enterprise AI Support Agent (RAG-Based)

An enterprise-style AI support agent that answers customer support questions using
**retrieval-augmented generation (RAG)**, **LLM-based intent classification**, and
**explicit decision logic**. 

---

## Features

- **LLM-based intent classification**
  - Classifies queries into billing, technical support, service terms, production or escalation.
- **Retrieval-Augmented Generation (RAG)**
  - Uses sentence-transformer embeddings and FAISS for semantic search
- **Escalation handling**
  - Automatically defers to a human agent when confidence is low
- **OpenAI-compatible API**
  - Exposes the agent via a `/v1/chat/completions` endpoint
  - Enables seamless integration with Open WebUI and other OpenAI-compatible tools
- **Multiple interfaces**
  - Open WebUI for a full-featured chat experience
  - Streamlit UI for lightweight local demos
- **Evaluation utilities**
  - Intent accuracy and retrieval sanity checks

---

## Architecture Overview

```text
User Query
   ↓
(Open WebUI / Streamlit / API Client)
   ↓
OpenAI-Compatible FastAPI Endpoint
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

## Example Conversation

Below is an example interaction with the support agent using **Open WebUI**.
The agent identifies intent, retrieves relevant billing policy documents, and generates
a grounded response based solely on retrieved context.

![Open WebUI Conversation Example](data/sample-conversation.png)

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

2. Launch the UI (See steps below for Open WebUI)
```bash
streamlit run ui/streamlit_app.py
```

---

### Using Open WebUI

#### Prerequisites
  - Docker https://www.docker.com/products/docker-desktop/ 
  - Ollama (with Gemma pulled locally)

#### Run Open WebUI with docker
  ```bash
  docker run -d \
    -p 3000:8080 \
    -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
    --name open-webui \
    ghcr.io/open-webui/open-webui:main
  ```

#### Configure Open WebUI

  1. Open http://localhost:3000

  2. Create Admin account on Open WebUI

  3. Go to Admin Panel -> Settings ->  Connections -> OpenAI

      Set:

      API Base URL: http://host.docker.internal:8000/v1

      API Key: any value (not validated)

  4. Save and start chatting

---

## Evaluation

Run basic evaluation checks:
```bash
python eval/evaluate.py
```

---

## Possible Future Enhancements

- Query rewriting for improved retrieval

- Confidence scoring for responses

- LLM-based evaluation

- Persistent conversation memory
