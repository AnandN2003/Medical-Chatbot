"""
Store Index Script
Creates and stores document embeddings in Pinecone vector database.
This script should be run to initialize or update the vector database.
"""

import os
from dotenv import load_dotenv
from data_loader import process_documents
from embeddings import get_embedding_model, get_embedding_dimension
from vector_store import PineconeManager


def store_index(data_path: str = "data", 
                index_name: str = "medical-chatbot",
                chunk_size: int = 500,
                chunk_overlap: int = 20):
    """
    Main function to process documents and store them in Pinecone.
    
    Args:
        data_path: Path to directory containing PDF files
        index_name: Name for the Pinecone index
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
    """
    print("\n" + "="*60)
    print("📦 STORE INDEX - Creating Vector Database")
    print("="*60)
    
    # Load environment variables
    load_dotenv()
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    
    if not PINECONE_API_KEY:
        print("❌ Error: PINECONE_API_KEY not found in .env file")
        return
    
    print(f"\n✅ Pinecone API key loaded")
    
    # Step 1: Process documents
    print(f"\n{'='*60}")
    print("STEP 1: Processing Documents")
    print('='*60)
    chunks = process_documents(data_path, chunk_size, chunk_overlap)
    
    # Step 2: Load embedding model
    print(f"\n{'='*60}")
    print("STEP 2: Loading Embedding Model")
    print('='*60)
    embedding = get_embedding_model()
    embedding_dim = get_embedding_dimension()
    
    # Step 3: Setup Pinecone
    print(f"\n{'='*60}")
    print("STEP 3: Setting up Pinecone")
    print('='*60)
    pinecone_manager = PineconeManager(PINECONE_API_KEY, index_name)
    pinecone_manager.create_index(dimension=embedding_dim)
    
    # Step 4: Store vectors
    print(f"\n{'='*60}")
    print("STEP 4: Storing Vectors")
    print('='*60)
    vector_store = pinecone_manager.setup_vector_store(embedding, chunks)
    
    # Print summary
    print(f"\n{'='*60}")
    print("✅ SUMMARY")
    print('='*60)
    print(f"📄 Total documents processed: {len(chunks)}")
    print(f"📊 Total vectors in index: {pinecone_manager.get_vector_count()}")
    print(f"🏷️ Index name: {index_name}")
    print(f"✨ Vector database is ready for queries!")
    print('='*60 + "\n")
    
    return vector_store


if __name__ == "__main__":
    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Run the indexing process
    store_index()
