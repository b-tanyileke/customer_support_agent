"""
This module evaluates the performance of the Support Agent by running a set of test cases.
It measures intent classification accuracy, retrieval accuracy, and unexpected escalations.
"""

import json
from agent.intent_classifier import classify_intent
from agent.retriever import retrieve


def _normalize_source(source: str) -> str:
    normalized = (
        source.lower()
        .replace(".pdf", "")
        .replace(".txt", "")
        .replace("-", "_")
    )
    aliases = {"service_terms": "service_term"}
    return aliases.get(normalized, normalized)


# Load test cases
with open("data/test_questions.json", encoding="utf-8") as f:
    test_cases = json.load(f)

intent_correct = 0
retrieval_top1_correct = 0
retrieval_top3_correct = 0
unexpected_escalations = 0
rows = []

for case in test_cases:
    predicted = classify_intent(case["question"])
    if predicted == case["category"]:
        intent_correct += 1
    if predicted == "Escalate" and case["category"] != "Escalate":
        unexpected_escalations += 1

    chunks = retrieve(case["question"])
    expected_source = _normalize_source(case["source_document"])
    retrieved_sources = [_normalize_source(chunk["source"]) for chunk in chunks]

    top1_hit = bool(retrieved_sources and retrieved_sources[0] == expected_source)
    top3_hit = expected_source in retrieved_sources

    retrieval_top1_correct += int(top1_hit)
    retrieval_top3_correct += int(top3_hit)

    rows.append(
        {
            "id": case["id"],
            "expected_intent": case["category"],
            "predicted_intent": predicted,
            "expected_source": expected_source,
            "retrieved_sources": ", ".join(retrieved_sources),
            "top1_hit": top1_hit,
            "top3_hit": top3_hit,
        }
    )

accuracy = intent_correct / len(test_cases)
top1_accuracy = retrieval_top1_correct / len(test_cases)
top3_accuracy = retrieval_top3_correct / len(test_cases)

print(f"Intent Classification Accuracy: {accuracy:.2f}")
print(f"Retrieval Top-1 Source Hit Rate: {top1_accuracy:.2f}")
print(f"Retrieval Top-3 Source Hit Rate: {top3_accuracy:.2f}")
print(f"Unexpected Escalations: {unexpected_escalations}")

print("\nDetailed Results")
print("-" * 100)
for row in rows:
    print(
        f"{row['id']}: intent {row['predicted_intent']} "
        f"(expected {row['expected_intent']}), "
        f"source top1={row['top1_hit']} top3={row['top3_hit']}, "
        f"retrieved=[{row['retrieved_sources']}]"
    )
