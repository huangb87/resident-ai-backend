import asyncio
from app.ai.embeddings import PineconeService

async def clear_namespace():
    # Initialize PineconeService with the appropriate namespace
    pinecone_service = PineconeService(namespace="tenant1")
    
    # Delete all vectors in the namespace
    pinecone_service.index.delete(delete_all=True, namespace=pinecone_service.namespace)

# Run the clearing process
asyncio.run(clear_namespace())
