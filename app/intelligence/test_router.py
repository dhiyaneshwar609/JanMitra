from app.intelligence.query_router import QueryRouter

router = QueryRouter()

queries = [
    "PM Kisan eligibility",
    "Scholarships for students",
    "PM Kisan vs PMFBY",
    "Documents required?"
]

for q in queries:

    result = router.process(q)

    print("=" * 60)
    print("Query :", result["query"])
    print("Intent:", result["intent"].value)
    print("Plan  :", result["plan"])