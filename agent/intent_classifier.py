"""
Intent classifier module that uses a local LLM to classify user queries into predefined intents.
"""

from .prompts import INTENT_CLASSIFIER_PROMPT
from .llm_client import LLMError, generate


VALID_INTENTS = {
    "billing": "Billing",
    "technical support": "Technical Support",
    "products": "Products",
    "service terms": "Service Terms",
    "escalate": "Escalate",
}


def classify_intent(query: str) -> str:
    """
    Classifies user intent using a local LLM
    
    :param query: User Query
    :type query: str
    :return: Intent label
    :rtype: str
    """
    prompt = INTENT_CLASSIFIER_PROMPT.format(query=query)

    try:
        raw_intent = generate(prompt)
    except LLMError:
        return "Escalate"

    normalized = raw_intent.strip().lower()
    return VALID_INTENTS.get(normalized, "Escalate")


# Uncomment this line for rule based intent classification
# def classify_intent(query: str) -> str:
#     """
#     This function works to identify the intent in a user's message to the assistant.
#     This version works with simple if/else statements.
    
#     :param query: User question
#     :type query: str
#     :return: Intent label
#     :rtype: str
#     """

#     q = query.lower()
#     if any(word in q for word in ["bill", "payment", "charged", "refund"]):
#         return "Billing"
#     if any(word in q for word in ["device", "phone", "not working", "signal"]):
#         return "Technical Support"
#     if any(word in q for word in ["policy", "terms", "agreement", "contract"]):
#         return "Policy"
#     return "Escalate"
