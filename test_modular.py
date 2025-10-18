"""
Test script to verify the modular structure works correctly.
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.chdir(project_root)

print(f"📁 Working directory: {os.getcwd()}\n")

# Test imports
try:
    print("Testing imports...")
    from src.data_loader import process_documents
    from src.embeddings import get_embedding_model
    from src.vector_store import PineconeManager
    from src.llm_config import LLMConfig
    from src.query_engine import QueryEngine
    from dotenv import load_dotenv
    
    print("✅ All imports successful!\n")
    
    # Load environment variables
    load_dotenv()
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    print("🔑 API Keys:")
    print(f"   Pinecone: {'✅ Found' if PINECONE_API_KEY else '❌ Missing'}")
    print(f"   Gemini: {'✅ Found' if GEMINI_API_KEY else '❌ Missing'}\n")
    
    if PINECONE_API_KEY and GEMINI_API_KEY:
        # Test embedding
        print("Testing embedding model...")
        embedding = get_embedding_model()
        print("✅ Embedding model loaded\n")
        
        # Test Pinecone connection
        print("Testing Pinecone connection...")
        pm = PineconeManager(PINECONE_API_KEY, "medical-chatbot")
        vector_count = pm.get_vector_count()
        print(f"✅ Connected! Vectors in index: {vector_count}\n")
        
        # Test vector store
        print("Testing vector store...")
        vector_store = pm.setup_vector_store(embedding)
        print("✅ Vector store loaded\n")
        
        # Test retriever
        print("Testing retriever...")
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        print("✅ Retriever created\n")
        
        # Test LLM
        print("Testing Gemini LLM...")
        llm_model = LLMConfig.setup_gemini(GEMINI_API_KEY)
        print("✅ LLM initialized\n")
        
        # Test query engine
        print("Testing query engine...")
        query_engine = QueryEngine(llm_model, retriever)
        print("✅ Query engine created\n")
        
        # Test a simple query
        print("="*60)
        print("TESTING QUERY")
        print("="*60)
        test_question = "what is diabetes?"
        print(f"\n❓ Question: {test_question}\n")
        
        answer = query_engine.query(test_question)
        print(f"💡 Answer: {answer}\n")
        
        print("="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
