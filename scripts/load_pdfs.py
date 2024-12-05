"""
Script to load PDFs into knowledge base and test queries
"""
import os
import asyncio
from app.ai.pdf_loader import PDFProcessor

async def main():
    # Directory containing PDFs
    pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pdfs")
    
    # Create processor with a specific namespace
    processor = PDFProcessor(pdf_dir, namespace="tenant1")
    
    # Load PDFs into knowledge base
    print("Loading PDFs into knowledge base...")
    vector_ids = await processor.load_pdfs_to_knowledge_base()
    print(f"Loaded {len(vector_ids)} text chunks")
    
    # Test some queries
    test_queries = [
        "What is the main topic of the document?",
        "What are the key findings?",
    ]
    
    print("\nTesting queries...")
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = await processor.query_knowledge_base(query)
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Source: {result.metadata.get('source', 'Unknown')}")
            print(f"Page: {result.metadata.get('page', 'Unknown')}")
            print(f"Score: {result.score}")
            print(f"Text: {result.metadata.get('text', '')[:200]}...")

if __name__ == "__main__":
    asyncio.run(main())
