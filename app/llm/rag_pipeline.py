from click import prompt
from app.retrieval.faiss_retriever import FaissRetriever
from app.retrieval.confidence import ConfidenceEngine
from app.llm.local_llm import LocalLLM
from app.memory.memory import ConversationMemory
from app.llm.intent_router import IntentRouter
import time
import json
from app.retrieval.query_rewriter import QueryRewriter
from app.intelligence.query_router import QueryRouter
from app.utils.answer_formatter import AnswerFormatter
from app.intelligence.entity_extractor import EntityExtractor
from app.intelligence.language_detector import LanguageDetector
class RAGPipeline:
    

    def __init__(self):
        self.query_router = QueryRouter()
        self.query_rewriter = QueryRewriter()
        self.retriever = FaissRetriever()
        self.confidence_engine = ConfidenceEngine()
        self.llm = LocalLLM()
        self.memory = ConversationMemory()
        self.intent_router = IntentRouter()
        self.entity_extractor = EntityExtractor()

        
        self.high_confidence = 0.80
        self.medium_confidence = 0.60
        self.low_confidence = 0.40
            

        self.max_context_chars = 2500

    # --------------------------------------------------
    # Build Context
    # --------------------------------------------------

    def build_context(self, results):

        context = ""

        for doc in results:

            text = doc["content"].strip()

            if len(context) + len(text) > self.max_context_chars:
                break

            context += text
            context += "\n\n"

        return context

    # --------------------------------------------------
    # Collect Sources
    # --------------------------------------------------

    def collect_sources(self, results):

        sources = []
        added = set()

        for doc in results:

            key = (doc["title"], doc["url"])

            if key not in added:

                sources.append(
                    {
                        "title": doc["title"],
                        "url": doc["url"]
                    }
                )

                added.add(key)

        return sources

    # --------------------------------------------------
    # Confidence Level
    # --------------------------------------------------

    def get_confidence_level(self, confidence):

        if confidence >= self.high_confidence:
            return "HIGH"

        elif confidence >= self.medium_confidence:
            return "MEDIUM"

        elif confidence >= self.low_confidence:
            return "LOW"

        return "VERY LOW"

    # --------------------------------------------------
    # Prompt Builder
    # --------------------------------------------------

    def build_prompt(self, question, context, history):

        return f"""
    You are JanMitra AI, an AI assistant for Government of India and State Government schemes.

    Your ONLY source of information is the Knowledge Context below.

    ========================
    RULES
    ========================

    

    1. Answer ONLY using the Knowledge Context.
    2. Never use outside knowledge or assumptions.
    3. If the answer is not present, say:
    "The requested information is not available in the retrieved government documents."
    4. Do not mix information from different schemes.
    5. Create only the headings supported by the context.
    6. Use plain text headings with the specified icons.

    ========================
    PREVIOUS CONVERSATION
    ========================

    {history}

    ========================
    KNOWLEDGE CONTEXT
    ========================

    {context}

    ========================
    USER QUESTION
    ========================

    {question}

    ========================
RESPONSE FORMAT
========================

Answer ONLY using the information explicitly available in the Knowledge Context.

Formatting Rules:

• If the context contains information such as:
📍 Overview
👤 Eligibility
🎁 Benefits
📑 Required Documents
🖋️ Application Process
🌐 Official Sources

  then present those sections using clear headings.
  Use plain text headings only.

Example:

📍 Overview:

👤 Eligibility:

🎁 Benefits:

📄 Required Documents:

📝 Application Process:

🌐 Official Sources:
Rules:

• Do NOT use Markdown symbols (#, ##, ###, **).
• Do NOT create headings for information that is not present.
• Never use outside knowledge.
• Never guess or infer missing information.
• Do not mix information from different government schemes.
• Every statement must be supported by the retrieved context.
• If the requested information is not available, reply:

"The requested information is not available in the retrieved government documents."

• For follow-up questions:
  - Answer only the specific question.
  - Do not repeat the full scheme description unless requested.

• Keep the response concise, factual, professional, and complete.
• Finish every sentence before ending the response.

========================
ANSWER
========================

"""

        
        # --------------------------------------------------
    # Ask
    # --------------------------------------------------

    def stream_answer(self, question):
        total_start = time.time()

        # -----------------------------------------
        # Automatic Language Detection
        # -----------------------------------------

        detected_language = LanguageDetector.detect(question)

        print("\n========== LANGUAGE DETECTION ==========")
        print("Input    :", question)
        print("Language :", detected_language)
        print("========================================")
        # -----------------------------------------
        # Rewrite Follow-up Queries
        # -----------------------------------------

        last_entity = self.memory.get_last_entity()

        question = self.query_rewriter.rewrite(
            question,
            last_entity
        )
        routing = self.query_router.process(question)

        print("\n========== QUERY ROUTER ==========")
        print("Intent :", routing["intent"])
        print("Plan   :", routing["plan"])
        print("==================================")

        print("Rewritten Query:", question)
        # -----------------------------------------
        # Intent Routing
        # -----------------------------------------

        intent_result = self.intent_router.route(question)

        if intent_result["intent"] != "RAG":

            return {
                "answer": intent_result["response"],
                "confidence": 100.0,
                "confidence_level": "DIRECT",
                "sources": []
            }

        # -----------------------------------------
        # Retrieve Documents
        # -----------------------------------------

        retrieval_start = time.time()

        results = self.retriever.retrieve(question)

        print(f"\nRetrieval Time : {time.time() - retrieval_start:.2f} seconds")

        print("\n" + "=" * 70)
        print("RETRIEVED DOCUMENTS")
        print("=" * 70)

        for i, doc in enumerate(results, start=1):

            print(f"\nDocument {i}")
            print(f"Title    : {doc['title']}")
            print(f"Distance : {doc['distance']:.4f}")
            print(doc["content"][:250])

        # -----------------------------------------
        # Previous Conversation
        # -----------------------------------------

        history = self.memory.get_context()

        # -----------------------------------------
        # Build Context
        # -----------------------------------------

        context_start = time.time()

        context = self.build_context(results)
        print("\n========== FULL CONTEXT ==========")
        print(context)
        print("==================================")

        print(f"Context Size : {len(context)} characters")
        print(f"Context Build Time : {time.time() - context_start:.2f} seconds")

        # -----------------------------------------
        # Confidence
        # -----------------------------------------

        confidence = self.confidence_engine.calculate(
            question,
            results
        )

        confidence_level = self.get_confidence_level(
            confidence
        )

        print("\n" + "=" * 70)
        print("CONFIDENCE ANALYSIS")
        print("=" * 70)
        print(f"Score : {confidence:.3f}")
        print(f"Level : {confidence_level}")

        # -----------------------------------------
        # Build Prompt
        # -----------------------------------------

        prompt = self.build_prompt(
            question,
            context,
            history
        )
        # -----------------------------------------
        # Language Instruction
        # -----------------------------------------

        language_instruction = f"""
        LANGUAGE REQUIREMENT:
        The user's detected language is {detected_language}.

        Answer the user in {detected_language}.

        Do not change the answer to English unless the user asks for English.

        Use clear, natural {detected_language} suitable for an ordinary citizen.

        Use ONLY the information available in the provided context.
        """

        prompt = prompt + "\n\n" + language_instruction

        # -----------------------------------------
        # Generate Answer
        # -----------------------------------------

        # -----------------------------------------
# Generate Answer
# -----------------------------------------

        llm_start = time.time()

        print("\n" + "=" * 70)
        print(f"Prompt Size : {len(prompt)} characters")
        print("=" * 70)

        full_answer = ""


        for chunk in self.llm.stream(prompt):

            full_answer += chunk

            yield json.dumps({
                "type": "chunk",
                "data": chunk
            }) + "\n"

        print(f"\nLLM Time : {time.time() - llm_start:.2f} seconds")

        if not full_answer.strip():
            full_answer = (
                "The requested information is not available "
                "in the current knowledge base."
            )

        answer = AnswerFormatter.format(full_answer.strip())

        # -----------------------------------------
        # Collect Sources
        # -----------------------------------------

        sources = self.collect_sources(results)

        # -----------------------------------------
        # Save Conversation
        # -----------------------------------------

        entity = self.entity_extractor.extract(
            question,
            self.memory.get_last_entity()
        )

        self.memory.add(
            question,
            answer,
            entity
        )

        print("\n" + "=" * 60)
        print(f"TOTAL PIPELINE TIME : {time.time() - total_start:.2f} seconds")
        print("=" * 60)
        yield json.dumps({
    "type": "done",
    "sources": sources
}) + "\n"