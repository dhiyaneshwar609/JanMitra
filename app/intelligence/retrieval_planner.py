from dataclasses import dataclass

from app.intelligence.intent_classifier import IntentType


@dataclass
class RetrievalPlan:
    """
    Defines how retrieval should be performed.
    """

    top_k: int
    use_memory: bool = False
    separate_entities: bool = False
    rerank: bool = True


class RetrievalPlanner:
    """
    Converts an intent into a retrieval strategy.

    This class DOES NOT perform retrieval.
    It only decides how retrieval should happen.
    """

    def create_plan(self, intent: IntentType) -> RetrievalPlan:

        if intent == IntentType.SPECIFIC:
            return RetrievalPlan(
                top_k=2,
                use_memory=False,
                separate_entities=False,
                rerank=True,
            )

        elif intent == IntentType.DISCOVERY:
            return RetrievalPlan(
                top_k=8,
                use_memory=False,
                separate_entities=False,
                rerank=True,
            )

        elif intent == IntentType.COMPARISON:
            return RetrievalPlan(
                top_k=3,
                use_memory=False,
                separate_entities=True,
                rerank=True,
            )

        elif intent == IntentType.FOLLOW_UP:
            return RetrievalPlan(
                top_k=2,
                use_memory=True,
                separate_entities=False,
                rerank=True,
            )

        # Safe default
        return RetrievalPlan(
            top_k=2,
            use_memory=False,
            separate_entities=False,
            rerank=True,
        )