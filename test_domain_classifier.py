from app.classifier.domain_classifier import DomainClassifier

classifier = DomainClassifier()

questions = [

    "What is PM Kisan?",

    "How can I apply for Aadhaar?",

    "What are the benefits of PM Vishwakarma?",

    "Scholarship for engineering students",

    "Hospital under Ayushman Bharat",

    "How to register GST?",

    "Driving licence renewal",

    "MSME registration",

    "Tell me IPL score",

    "Write Python program"

]

for question in questions:

    result = classifier.classify(question)

    print("=" * 70)

    print("Question :", question)

    print("Supported:", result["supported"])

    print("Best Domain:", result["best_domain"])

    print("Confidence:", result["confidence"])

    print("Top Domains:")

    for domain, score in result["top_domains"]:
        print(f"   {domain:25} {score:.4f}")