"""
Main agent logic that handles user queries end-to-end
"""

# Import necessary libraries
import subprocess
from agent.intent_classifier import classify_intent
from agent.prompts import SUPPORT_PROMPT
from agent.retriever import retrieve


def call_gemma(prompt: str) -> str:
    """
    Calls gemma locally via ollama
    
    :param prompt: Prompt sent to the LLM
    :type prompt: str
    :return: Model response
    :rtype: str
    """

    result = subprocess.run(
        ["ollama", "run", "gemma", prompt],
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",      # force UTF-8
        errors="replace"
    )
    return result.stdout.strip()


def handle_query(query: str) -> str:
    """
    Docstring for handle_query
    
    :param query: User question
    :type query: str
    :return: Agent response
    :rtype: str
    """

    # 1. Classify user intent
    intent = classify_intent(query)

    # 2. Escalation handling
    if intent == "escalate":
        return( "This issue may require a human support agent. "
            "Please contact customer support for further assistance."
            )

    # 3. Retrieve relevant documents
    retrieved_chunks = retrieve(query)
    context = "\n\n".join(retrieved_chunks)

    # 4. Generate grounded response
    prompt = SUPPORT_PROMPT.format(
        context=context,
        question=query
    )
    response = call_gemma(prompt)

    return response
