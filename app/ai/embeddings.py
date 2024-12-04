"""
Vector embeddings and Pinecone service for knowledge base management
"""
from typing import List, Dict, Any
import pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from app.core.config import settings

class PineconeService:
    def __init__(self):
        # Initialize Pinecone
        pinecone.init(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT
        )
        
        # Initialize the index (create if doesn't exist)
        self.index_name = "whatsapp-ai-kb"
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=self.index_name,
                dimension=1536,  # OpenAI embedding dimension
                metric="cosine"
            )
            
        self.index = pinecone.Index(self.index_name)
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        
    async def add_texts(
        self,
        texts: List[str],
        metadata: List[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Add texts to the vector store
        
        Args:
            texts: List of text strings to embed and store
            metadata: Optional list of metadata dicts for each text
            
        Returns:
            List of IDs for stored vectors
        """
        # Generate embeddings
        embeddings = await self.embeddings.aembed_documents(texts)
        
        # Prepare vectors with metadata
        vectors = []
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            metadata_dict = metadata[i] if metadata else {"text": text}
            vectors.append((
                f"vec_{i}",  # Vector ID
                embedding,
                metadata_dict
            ))
            
        # Upsert to Pinecone
        self.index.upsert(vectors=vectors)
        
        return [v[0] for v in vectors]
        
    async def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar texts
        
        Args:
            query: Query text
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of similar items with scores and metadata
        """
        # Generate query embedding
        query_embedding = await self.embeddings.aembed_query(query)
        
        # Search in Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=k,
            include_metadata=True,
            filter=filter
        )
        
        # Format results
        formatted_results = []
        for match in results.matches:
            formatted_results.append({
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata
            })
            
        return formatted_results
        
    async def delete_texts(self, ids: List[str]) -> None:
        """
        Delete vectors by their IDs
        
        Args:
            ids: List of vector IDs to delete
        """
        try:
            self.index.delete(ids=ids)
        except pinecone.errors.NotFoundError:
            print(f"Vector IDs {ids} not found in the index.")
        except pinecone.errors.PineconeError as e:
            print(f"Error deleting vector IDs {ids}: {e}")
