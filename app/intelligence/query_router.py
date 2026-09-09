from app.intelligence.intent_classifier import IntentClassifier
from app.intelligence.retrieval_planner import RetrievalPlanner
from app.intelligence.conversation_memory import ConversationMemory


class QueryRouter:
    """
    Orchestrates the Intelligence Layer.

    Flow:
        User Query
            ↓
        Intent Classification
            ↓
        Retrieval Planning
            ↓
        Conversation Memory
            ↓
        Return routing information
    """

    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.retrieval_planner = RetrievalPlanner()
        self.memory = ConversationMemory()

    def process(self, query: str):

        # Step 1: Detect intent
        intent_result = self.intent_classifier.classify(query)

        # Step 2: Create retrieval plan
        plan = self.retrieval_planner.create_plan(intent_result.intent)

        # Step 3: Resolve follow-up queries
        final_query = query

        if plan.use_memory:
            final_query = self.memory.resolve_follow_up(query)

        return {
            "query": final_query,
            "intent": intent_result.intent,
            "confidence": intent_result.confidence,
            "plan": plan,
        }