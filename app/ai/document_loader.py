"""
Document Loader for processing and loading documents into the knowledge base
"""
from typing import List, Dict, Any
import os
import json
from app.ai.embeddings import PineconeService

class DocumentLoader:
    def __init__(self, directory: str):
        self.directory = directory
        self.pinecone_service = PineconeService()

    def load_documents(self) -> List[Dict[str, Any]]:
        """
        Load and preprocess documents from the specified directory
        
        Returns:
            List of document data with metadata
        """
        documents = []
        
        for filename in os.listdir(self.directory):
            if filename.endswith(".json"):
                file_path = os.path.join(self.directory, filename)
                with open(file_path, "r") as file:
                    document_data = json.load(file)
                    documents.append(document_data)
        
        return documents

    def preprocess_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess a single document
        
        Args:
            document: Raw document data
            
        Returns:
            Preprocessed document data
        """
        # Example preprocessing: lowercasing text
        document["text"] = document["text"].lower()
        return document

    def load_and_preprocess(self) -> List[Dict[str, Any]]:
        """
        Load, preprocess, and return documents
        
        Returns:
            List of preprocessed document data
        """
        raw_documents = self.load_documents()
        preprocessed_documents = [self.preprocess_document(doc) for doc in raw_documents]
        return preprocessed_documents

    def load_and_store_documents(self) -> List[str]:
        """
        Load, preprocess, and store documents in Pinecone
        
        Returns:
            List of IDs for stored documents
        """
        preprocessed_documents = self.load_and_preprocess()
        texts = [doc['text'] for doc in preprocessed_documents]
        metadata = [{'filename': doc.get('filename', 'unknown')} for doc in preprocessed_documents]
        
        # Store in Pinecone
        ids = self.pinecone_service.add_texts(texts, metadata)
        return ids
