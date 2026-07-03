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
    except LLMError as exc:
        return _rule_based_intent(query, error=exc)

    normalized = raw_intent.strip().lower()
    return VALID_INTENTS.get(normalized, _rule_based_intent(query))


def _rule_based_intent(query: str, error: Exception | None = None) -> str:
    """
    Small fallback so demos still behave sensibly if the classifier LLM is unavailable.
    """
    q = query.lower()
    if any(word in q for word in ["bill", "billing", "payment", "charged", "refund", "autopay", "auto-pay", "fee", "dispute"]):
        return "Billing"
    if any(word in q for word in ["device", "phone", "signal", "service", "sms", "text", "warranty", "screen", "sim"]):
        return "Technical Support"
    if any(word in q for word in ["plan", "product", "netflix", "hotspot", "data", "catalog"]):
        return "Products"
    if any(word in q for word in ["terms", "policy", "unlock", "agreement", "privacy", "location", "account"]):
        return "Service Terms"
    if error is not None:
        print(f"Intent classifier LLM unavailable; using fallback. Error: {error}")
    return "Escalate"


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
