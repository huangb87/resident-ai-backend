"""
Vector embeddings and Pinecone service for knowledge base management
"""
from typing import List, Dict, Any, Optional
from pinecone.grpc import PineconeGRPC as Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self, namespace: str = "default"):
        self.index_name = "whatsapp-ai-kb"
        self.namespace = namespace
        
        # Debug logging
        logger.info(f"Using index name: {self.index_name}")
        logger.info(f"Using namespace: {self.namespace}")
        
        # Initialize Pinecone with GRPC client
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        # Connect to the index
        self.index = self.pc.Index(self.index_name)
        logger.info("Successfully connected to Pinecone index")
        
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
    
    async def add_texts(
        self,
        texts: List[str],
        ids: List[str],
        namespace: str,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """Add texts to the vector store."""
        if metadatas is None:
            metadatas = [{} for _ in texts]

        # Generate embeddings using OpenAI
        embeddings = await self.embeddings.aembed_documents(texts)

        # Prepare records for upsert
        records = [{
            "id": id,
            "values": embedding,
            "metadata": metadata
        } for id, embedding, metadata in zip(ids, embeddings, metadatas)]

        # Upsert records in batches
        vector_ids = []
        batch_size = 100
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            try:
                response = self.index.upsert(
                    vectors=batch,
                    namespace=namespace
                )
                vector_ids.append(response.upserted_count)
            except Exception as e:
                logger.error(f"Error upserting batch: {e}")
        return vector_ids
    
    async def similarity_search(
        self,
        query: str,
        k: int = 4,
    ) -> List[Dict[str, Any]]:
        """Search for similar texts using a query string."""
        # Get the embedding for the query
        query_embedding = await self.embeddings.aembed_query(query)
        
        # Query the index with namespace
        results = self.index.query(
            vector=query_embedding,
            top_k=k,
            namespace=self.namespace,
            include_metadata=True
        )
        
        return results.matches
        
    async def delete_texts(self, ids: List[str]) -> None:
        """
        Delete vectors by their IDs
        
        Args:
            ids: List of vector IDs to delete
        """
        try:
            self.index.delete(ids=ids, namespace=self.namespace)
        except pinecone.errors.NotFoundError:
            print(f"Vector IDs {ids} not found in the index.")
        except pinecone.errors.PineconeError as e:
            print(f"Error deleting vector IDs {ids}: {e}")
