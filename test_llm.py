from app.llm.local_llm import LocalLLM

llm = LocalLLM()

question = "What is Artificial Intelligence?"

answer = llm.generate(question)

print("\nQuestion:")
print(question)

print("\nAnswer:")
print(answer)