"""
Run Chatbot Script
Main script to run the medical chatbot with interactive queries.
"""

import os
from dotenv import load_dotenv
from embeddings import get_embedding_model
from vector_store import PineconeManager
from llm_config import LLMConfig
from query_engine import QueryEngine


def run_chatbot(index_name: str = "medical-chatbot",
                model_name: str = "models/gemini-2.5-flash",
                interactive: bool = True,
                auto_create_index: bool = True):
    """
    Run the medical chatbot.
    
    Args:
        index_name: Name of the Pinecone index
        model_name: Name of the Gemini model
        interactive: Whether to run in interactive mode
        auto_create_index: If True, creates index and processes docs if it doesn't exist
    """
    print("\n" + "="*60)
    print("🩺 MEDICAL CHATBOT")
    print("="*60)
    
    # Load environment variables
    load_dotenv()
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Check API keys
    print("\n🔑 API Key Status:")
    print(f"   PINECONE_API_KEY: {'✅ Found' if PINECONE_API_KEY else '❌ Not found'}")
    print(f"   GEMINI_API_KEY: {'✅ Found' if GEMINI_API_KEY else '❌ Not found'}")
    
    if not PINECONE_API_KEY or not GEMINI_API_KEY:
        print("\n❌ Error: Required API keys not found in .env file")
        return
    
    # Setup embedding model
    print(f"\n{'='*60}")
    print("Loading Embedding Model")
    print('='*60)
    embedding = get_embedding_model()
    from embeddings import get_embedding_dimension
    embedding_dim = get_embedding_dimension()
    
    # Setup Pinecone
    print(f"\n{'='*60}")
    print("Connecting to Vector Database")
    print('='*60)
    pinecone_manager = PineconeManager(PINECONE_API_KEY, index_name)
    
    # Check if index exists and create if needed
    from data_loader import process_documents
    
    # Create index if it doesn't exist
    pinecone_manager.create_index(dimension=embedding_dim)
    
    # Check if index has data
    vector_count = pinecone_manager.get_vector_count()
    
    if vector_count == 0 and auto_create_index:
        print("\n⚠️ Index is empty. Processing documents from 'data/' folder...")
        print(f"{'='*60}")
        chunks = process_documents("data/")
        vector_store = pinecone_manager.setup_vector_store(embedding, chunks)
        print(f"{'='*60}")
        print(f"✅ Added {len(chunks)} document chunks to the index")
    else:
        vector_store = pinecone_manager.setup_vector_store(embedding)
    
    # Create retriever
    print("\n🔍 Creating retriever...")
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )
    print("   ✅ Retriever ready")
    
    # Setup LLM
    print(f"\n{'='*60}")
    print("Initializing Language Model")
    print('='*60)
    llm_model = LLMConfig.setup_gemini(GEMINI_API_KEY, model_name)
    
    # Create query engine
    print("\n⚙️ Setting up query engine...")
    query_engine = QueryEngine(llm_model, retriever)
    print("   ✅ Query engine ready")
    
    # Test query
    if not interactive:
        print(f"\n{'='*60}")
        print("Testing with Sample Query")
        print('='*60)
        test_question = "what is Acromegaly and gigantism?"
        print(f"\n❓ Question: {test_question}")
        
        result = query_engine.query(test_question, return_sources=True)
        print(f"\n💡 Answer: {result['answer']}")
        print(f"\n📚 Sources: {', '.join(set(result['sources']))}")
        print("\n✅ Chatbot is working correctly!")
    else:
        # Interactive mode
        query_engine.interactive_query()
    
    return query_engine


if __name__ == "__main__":
    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Run the chatbot in interactive mode
    run_chatbot(interactive=True)
