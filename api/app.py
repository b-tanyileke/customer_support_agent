"""
This module provides a FastAPI application that exposes endpoints compatible with OpenAI's API.
It allows users to query the support agent and receive responses in a format expected by OpenAI clients.
"""

import uuid
import time
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent.llm_client import LLMError, generate
from agent.support_agent import handle_query
from config import LLM_MODEL, LLM_PROVIDER, OLLAMA_BASE_URL

app = FastAPI(title="Enterprise AI Support Agent (OpenAI Compatible)")

# Request schemas
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    temperature: float | None = None
    max_tokens: int | None = None


class QueryRequest(BaseModel):
    question: str


# OpenAI-compatible endpoint

@app.get("/v1/models")
async def list_models():
    """Tells Open WebUI what models are available."""
    return {
        "object": "list",
        "data": [
            {"id": "support-agent", "object": "model", "owned_by": "local"},
            {"id": LLM_MODEL, "object": "model", "owned_by": "configured-provider"},
        ]
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "provider": LLM_PROVIDER,
        "model": LLM_MODEL,
        "ollama_base_url": OLLAMA_BASE_URL if LLM_PROVIDER == "ollama" else None,
    }


@app.get("/health/llm")
async def health_llm():
    """Checks whether the configured LLM provider is reachable."""
    try:
        response = generate("Respond with exactly: OK")
    except LLMError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "status": "ok",
        "provider": LLM_PROVIDER,
        "model": LLM_MODEL,
        "response": response,
    }


@app.post("/query")
async def query(request: QueryRequest) -> Dict[str, Any]:
    """Handle a simple query request."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    return handle_query(request.question)


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest) -> Dict[str, Any]:
    """
    OpenAI-compatible chat completion endpoint.
    Open WebUI will call this endpoint.
    """

    # Extract the latest user message
    user_message = None
    for msg in reversed(request.messages):
        if msg.role == "user":
            user_message = msg.content
            break

    if user_message is None:
        raise HTTPException(status_code=400, detail="No user message provided.")

    agent_response = handle_query(user_message)

    # Build OpenAI-style response
    response = {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": agent_response["response"]
                },
                "finish_reason": "stop"
            }
        ],
        "metadata": {
            "intent": agent_response["intent"],
            "sources": agent_response["sources"],
            "escalated": agent_response["escalated"],
        },
    }

    return response
