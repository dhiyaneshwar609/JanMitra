from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from app.intelligence.intent_classifier import IntentType


@dataclass
class ConversationContext:
    """
    Stores the most recent conversation context.
    """

    query: str
    entity: Optional[str]
    intent: IntentType
    timestamp: datetime


class ConversationMemory:
    """
    Lightweight conversation memory.

    Keeps only the latest context so follow-up
    questions can be resolved before retrieval.
    """

    def __init__(self):
        self._context: Optional[ConversationContext] = None

    def save_context(
        self,
        query: str,
        entity: Optional[str],
        intent: IntentType
    ) -> None:
        """
        Save the latest conversation context.
        """

        self._context = ConversationContext(
            query=query,
            entity=entity,
            intent=intent,
            timestamp=datetime.now()
        )

    def get_context(self) -> Optional[ConversationContext]:
        """
        Return the latest conversation context.
        """

        return self._context

    def clear(self) -> None:
        """
        Clear conversation memory.
        """

        self._context = None

    def resolve_follow_up(self, query: str) -> str:
        """
        Resolve a follow-up question using
        the stored entity.
        """

        if self._context is None:
            return query

        if self._context.entity:
            return f"{self._context.entity} {query}"

        return query