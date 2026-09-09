from app.intelligence.conversation_memory import ConversationMemory
from app.intelligence.intent_classifier import IntentType

memory = ConversationMemory()

memory.save_context(
    query="PM Kisan eligibility",
    entity="PM Kisan",
    intent=IntentType.SPECIFIC
)

print(memory.get_context())

print(memory.resolve_follow_up("Documents required?"))
print(memory.resolve_follow_up("Eligibility"))
print(memory.resolve_follow_up("How to apply?"))