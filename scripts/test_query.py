import asyncio
from app.ai.embeddings import PineconeService

async def test_query():
    # Initialize PineconeService with the appropriate namespace
    pinecone_service = PineconeService(namespace="tenant1")

    # Define the query
    query = "What happened at the latest AGM meeting?"

    # Perform the similarity search
    results = await pinecone_service.similarity_search(query=query, k=4)

    # Print the results
    for result in results:
        print(f"Score: {result['score']}, Metadata: {result['metadata']}")

# Run the test
asyncio.run(test_query())