"""
OpenAI-compatible API wrapper for the Enterprise AI Support Agent.
"""

import uuid
import time
from typing import List, Dict, Any, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from agent.support_agent import handle_query

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


# OpenAI-compatible endpoint

@app.get("/v1/models")
async def list_models():
    """Tells Open WebUI what models are available."""
    return {
        "object": "list",
        "data": [
            {"id": "support-agent", "object": "model", "owned_by": "local"}
        ]
    }

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
        return {
            "error": {
                "message": "No user message provided."
            }
        }

    # Call your existing agent
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
                    "content": agent_response
                },
                "finish_reason": "stop"
            }
        ]
    }

    return response
