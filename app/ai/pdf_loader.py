"""
PDF processing and knowledge base integration
"""
import os
from typing import List, Dict, Any
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.ai.embeddings import PineconeService

class PDFProcessor:
    def __init__(self, pdf_directory: str, namespace: str = "default"):
        """
        Initialize PDF processor
        
        Args:
            pdf_directory: Directory containing PDF files
            namespace: Namespace for vector storage (e.g., tenant ID or knowledge base name)
        """
        self.pdf_directory = pdf_directory
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.pinecone_service = PineconeService(namespace=namespace)
    
    async def load_pdfs_to_knowledge_base(self) -> List[str]:
        """
        Load all PDFs from directory into knowledge base
        
        Returns:
            List of vector IDs for stored chunks
        """
        all_chunks = []
        all_metadatas = []
        
        # Process each PDF file
        for filename in os.listdir(self.pdf_directory):
            if filename.endswith(".pdf"):
                file_path = os.path.join(self.pdf_directory, filename)
                
                # Load PDF
                loader = PyPDFLoader(file_path)
                pages = loader.load_and_split()
                
                # Split into chunks
                for page in pages:
                    chunks = self.text_splitter.split_text(page.page_content)
                    all_chunks.extend(chunks)
                    
                    # Create metadata for each chunk
                    for _ in chunks:
                        metadata = {
                            "source": filename,
                            "page": page.metadata.get("page", 0)
                        }
                        all_metadatas.append(metadata)
        
        # Store in Pinecone with metadata
        if all_chunks:
            # Generate unique IDs for each chunk
            ids = [f"{i}-{os.urandom(4).hex()}" for i in range(len(all_chunks))]
            
            vector_ids = await self.pinecone_service.add_texts(
                texts=all_chunks,
                ids=ids,
                namespace=self.pinecone_service.namespace,
                metadatas=all_metadatas
            )
            return vector_ids
        return []
    
    async def query_knowledge_base(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        Query the knowledge base
        
        Args:
            query: Query string
            k: Number of results to return
            
        Returns:
            List of similar chunks with metadata
        """
        results = await self.pinecone_service.similarity_search(query, k=k)
        return results
