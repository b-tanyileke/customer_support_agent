"""
Evaluates intent classification and retrieval effectiveness.
"""

import json
from agent.intent_classifier import classify_intent
from agent.retriever import retrieve


# Load test cases
with open("data/test_questions.json", encoding="utf-8") as f:
    test_cases = json.load(f)

intent_correct = 0

for case in test_cases:
    predicted = classify_intent(case["question"])
    if predicted == case["category"]:
        intent_correct += 1

accuracy = intent_correct / len(test_cases)

print(f"Intent Classification Accuracy: {accuracy:.2f}")

# Retrieval sanity check
for case in test_cases:
    chunks = retrieve(case["question"])
    print(f"\nQuestion: {case['question']}")
    print("Retrieved snippet:", chunks[0][:120])
