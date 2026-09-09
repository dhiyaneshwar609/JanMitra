from app.llm.rag_pipeline import RAGPipeline

rag = RAGPipeline()

print("=" * 60)
print("Language-Agnostic AI Assistant")
print("Type 'exit' to quit")
print("=" * 60)

while True:
    question = input("\nYou: ")

    if question.lower() == "exit":
        print("\nGoodbye!")
        break

    answer = rag.ask(question)

    print("\nAssistant:")
    print(answer)