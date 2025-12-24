"""
Classifies the user's intent so the agent can know what actions to take
"""

# Import Libraries
import subprocess
from agent.prompts import INTENT_CLASSIFIER_PROMPT


def classify_intent(query: str) -> str:
    """
    Classifies user intent using a local LLM
    
    :param query: User Query
    :type query: str
    :return: Intent label
    :rtype: str
    """
    prompt = INTENT_CLASSIFIER_PROMPT.format(query=query)

    # Call LLM and get intent
    result = subprocess.run(
        ["ollama", "run", "gemma", prompt],
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",      # force UTF-8
        errors="replace"
    )

    intent = result.stdout.strip()
    return intent


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
