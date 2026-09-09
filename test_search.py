from app.retrieval.retriever import search

query = input("Ask: ")

results = search(query)

if not results:
    print("\nNo relevant information found.")
else:

    for i, result in enumerate(results, start=1):

        print("=" * 80)

        print(f"Result {i}")
        print(f"Similarity : {result['score']}")
        print(f"Category   : {result['category']}")
        print(f"URL        : {result['url']}")
        print()

        print(result["content"])
        print()