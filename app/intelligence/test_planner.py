from app.intelligence.intent_classifier import IntentType
from app.intelligence.retrieval_planner import RetrievalPlanner

planner = RetrievalPlanner()

for intent in IntentType:
    plan = planner.create_plan(intent)

    print("=" * 40)
    print(intent.value)
    print(plan)