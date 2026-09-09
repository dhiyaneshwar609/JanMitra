from dataclasses import dataclass
from enum import Enum
import re


class IntentType(Enum):
    """Supported user intent types."""

    SPECIFIC = "specific"
    DISCOVERY = "discovery"
    COMPARISON = "comparison"
    FOLLOW_UP = "follow_up"


@dataclass
class IntentResult:
    intent: IntentType
    confidence: float


class IntentClassifier:
    """
    Rule-based intent classifier.

    Designed to be lightweight, fast, and easily replaceable
    by an ML/LLM classifier in the future.
    """

    def __init__(self):

        self.discovery_patterns = [
            r"\blist\b",
            r"\ball\b",
            r"\bschemes?\b",
            r"\bscholarships?\b",
            r"\bbenefits?\b",
            r"\bavailable\b",
            r"\bgovernment schemes?\b",
            r"\bprograms?\b",
            r"\bservices?\b",
        ]

        self.comparison_patterns = [
            r"\bvs\b",
            r"\bversus\b",
            r"\bcompare\b",
            r"\bdifference between\b",
            r"\bbetter than\b",
        ]

        self.followup_patterns = [
            r"\bdocuments?\b",
            r"\beligibility\b",
            r"\bapply\b",
            r"\bapplication\b",
            r"\bfees?\b",
            r"\bdeadline\b",
            r"\brequired\b",
            r"\bhow\b",
            r"\bwhen\b",
            r"\bwhere\b",
        ]

    def classify(self, query: str) -> IntentResult:

        query = query.lower().strip()

        # -------------------------
        # Comparison
        # -------------------------
        for pattern in self.comparison_patterns:
            if re.search(pattern, query):
                return IntentResult(
                    IntentType.COMPARISON,
                    0.98
                )

        # -------------------------
        # Discovery
        # -------------------------
        for pattern in self.discovery_patterns:
            if re.search(pattern, query):
                return IntentResult(
                    IntentType.DISCOVERY,
                    0.95
                )

        # -------------------------
        # Follow-up
        # -------------------------
        if len(query.split()) <= 5:
            for pattern in self.followup_patterns:
                if re.search(pattern, query):
                    return IntentResult(
                        IntentType.FOLLOW_UP,
                        0.90
                    )

        # -------------------------
        # Default
        # -------------------------
        return IntentResult(
            IntentType.SPECIFIC,
            0.99
        )