"""
Support agent module that handles user queries and returns responses.
This module integrates intent classification, document retrieval, 
and language model generation to provide answers to user questions.
"""

from agent.intent_classifier import classify_intent
from agent.llm_client import LLMError, generate
from agent.prompts import SUPPORT_PROMPT
from agent.retriever import RetrievalError, retrieve


ESCALATION_MESSAGE = (
    "This issue may require a human support agent. "
    "Please contact customer support for further assistance."
)


def handle_query(query: str) -> dict:
    """
    Handle a support query and return the answer plus useful metadata.
    """
    if not query or not query.strip():
        return {
            "response": "Please enter a support question.",
            "intent": "Escalate",
            "sources": [],
            "escalated": True,
        }

    intent = classify_intent(query)

    if intent == "Escalate":
        return {
            "response": ESCALATION_MESSAGE,
            "intent": intent,
            "sources": [],
            "escalated": True,
        }

    try:
        retrieved_chunks = retrieve(query)
    except RetrievalError as exc:
        return {
            "response": f"Knowledge base is unavailable: {exc}",
            "intent": intent,
            "sources": [],
            "escalated": True,
        }

    if not retrieved_chunks:
        return {
            "response": (
                "I could not find relevant support documentation for that question. "
                "Please contact a human support agent."
            ),
            "intent": intent,
            "sources": [],
            "escalated": True,
        }

    context = "\n\n".join(
        f"Source: {chunk['source']}\n{chunk['text']}" for chunk in retrieved_chunks
    )
    sources = _dedupe_sources(retrieved_chunks)

    prompt = SUPPORT_PROMPT.format(
        context=context,
        question=query
    )

    try:
        response = generate(prompt)
    except LLMError as exc:
        return {
            "response": f"Language model is unavailable: {exc}",
            "intent": intent,
            "sources": sources,
            "escalated": True,
        }

    return {
        "response": response,
        "intent": intent,
        "sources": sources,
        "escalated": False,
    }


def answer_query(query: str) -> str:
    """
    Compatibility helper for clients that only need the response text.
    """
    return handle_query(query)["response"]


def _dedupe_sources(chunks: list[dict]) -> list[dict]:
    seen = set()
    sources = []
    for chunk in chunks:
        source = chunk.get("source", "unknown")
        if source in seen:
            continue
        seen.add(source)
        sources.append({"source": source, "score": chunk.get("score")})
    return sources
