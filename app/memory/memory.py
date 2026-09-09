class ConversationMemory:

    def __init__(self, max_history=5):
        self.history = []
        self.max_history = max_history

    def add(self, question, answer, entity=None):

        self.history.append({
            "question": question,
            "answer": answer,
            "entity": entity
        })

        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_context(self):

        if not self.history:
            return ""

        conversation = []

        for item in self.history:

            conversation.append(
                f"User: {item['question']}"
            )

            conversation.append(
                f"Assistant: {item['answer']}"
            )

        return "\n".join(conversation)

    def get_last_entity(self):

        for item in reversed(self.history):

            if item.get("entity"):
                return item["entity"]

        return None

    def clear(self):
        self.history = []