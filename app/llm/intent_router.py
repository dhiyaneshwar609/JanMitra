import re


class IntentRouter:
    """
    Intent Router for CitizenAI.

    Returns:
        {
            "intent": "<intent_name>",
            "response": "<direct_response or None>"
        }
    """

    def __init__(self):

        self.intents = {

            "greeting": [
                "hi",
                "hello",
                "hey",
                "good morning",
                "good afternoon",
                "good evening"
            ],

            "identity": [
                "who are you",
                "what are you",
                "your name"
            ],

            "capability": [
                "what can you do",
                "how can you help",
                "features",
                "capabilities"
            ],

            "domains": [
                "supported domains",
                "what domains",
                "domains",
                "services"
            ],

            "thanks": [
                "thank you",
                "thanks",
                "thank u"
            ],

            "goodbye": [
                "bye",
                "goodbye",
                "see you"
            ]
        }

    # ------------------------------------------------

    def normalize(self, text):

        text = text.lower()
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # ------------------------------------------------

    def route(self, query):

        query = self.normalize(query)

        # Greeting
        for phrase in self.intents["greeting"]:
            if re.search(r"\b" + re.escape(phrase) + r"\b", query):
                return {
                    "intent": "GREETING",
                    "response": (
                        "Hello! I'm CitizenAI, your AI Public Service Assistant. "
                        "How can I help you today?"
                    )
                }

        # Identity
        for phrase in self.intents["identity"]:
            if re.search(r"\b" + re.escape(phrase) + r"\b", query):
                return {
                    "intent": "IDENTITY",
                    "response": (
                        "I am CitizenAI, an AI-powered Public Service Assistant "
                        "designed to help citizens with verified information about "
                        "government services, schemes, healthcare, education, "
                        "banking, taxation, agriculture, employment, and more."
                    )
                }

        # Capability
        for phrase in self.intents["capability"]:
            if re.search(r"\b" + re.escape(phrase) + r"\b", query):
                return {
                    "intent": "CAPABILITY",
                    "response": (
                        "I can help you with:\n\n"
                        "• Government Schemes\n"
                        "• Healthcare\n"
                        "• Education\n"
                        "• Banking\n"
                        "• Employment\n"
                        "• Agriculture\n"
                        "• Tax Services\n"
                        "• Identity Services\n"
                        "• Business Services\n"
                        "• Transport Services"
                    )
                }

        # Supported Domains
        for phrase in self.intents["domains"]:
            if re.search(r"\b" + re.escape(phrase) + r"\b", query):
                return {
                    "intent": "DOMAINS",
                    "response": (
                        "Currently I support:\n\n"
                        "• Government\n"
                        "• Government Schemes\n"
                        "• Healthcare\n"
                        "• Education\n"
                        "• Banking\n"
                        "• Employment\n"
                        "• Agriculture\n"
                        "• Taxation\n"
                        "• Identity Services\n"
                        "• Business\n"
                        "• Transport"
                    )
                }

        # Thanks
        for phrase in self.intents["thanks"]:
            if re.search(r"\b" + re.escape(phrase) + r"\b", query):
                return {
                    "intent": "THANKS",
                    "response": (
                        "You're welcome! I'm always here to help."
                    )
                }

        # Goodbye
        for phrase in self.intents["goodbye"]:
            if re.search(r"\b" + re.escape(phrase) + r"\b", query):
                return {
                    "intent": "GOODBYE",
                    "response": (
                        "Goodbye! Have a wonderful day."
                    )
                }

        # Default → Continue to RAG
        return {
            "intent": "RAG",
            "response": None
        }