from app.intelligence.intent_classifier import IntentClassifier

classifier = IntentClassifier()

queries = [
    "PM Kisan eligibility",
    "Scholarships for students",
    "Government schemes for farmers",
    "PM Kisan vs PMFBY",
    "Compare PMAY and PMFBY",
    "Documents required?",
    "How to apply?"
]

for q in queries:
    result = classifier.classify(q)
    print(f"{q:35} -> {result.intent.value} ({result.confidence})")