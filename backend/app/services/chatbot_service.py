"""
Chatbot Service
Business logic layer for chatbot operations.
"""

from typing import Optional
from app.core import (
    PineconeManager,
    LLMConfig,
    QueryEngine,
    get_embedding_model,
    get_embedding_dimension,
    process_documents
)
from app.config import settings


class ChatbotService:
    """Service class for managing chatbot operations."""
    
    def __init__(self):
        """Initialize the chatbot service."""
        self._pinecone_manager: Optional[PineconeManager] = None
        self._embedding_model = None
        self._vector_store = None
        self._llm_model = None
        self._query_engine: Optional[QueryEngine] = None
        self._initialized = False
    
    def initialize(self):
        """Initialize all chatbot components (lazy loading)."""
        if self._initialized:
            return
        
        print("\n🚀 Initializing Medical Chatbot Service...")
        
        # 1. Initialize Pinecone
        self._pinecone_manager = PineconeManager(
            api_key=settings.pinecone_api_key,
            index_name=settings.pinecone_index_name
        )
        
        # 2. Create or get index
        dimension = get_embedding_dimension(settings.embedding_model)
        self._pinecone_manager.create_index(
            dimension=dimension,
            metric=settings.pinecone_metric,
            cloud=settings.pinecone_cloud,
            region=settings.pinecone_region
        )
        
        # 3. Initialize embedding model
        self._embedding_model = get_embedding_model(settings.embedding_model)
        
        # 4. Check if we need to load documents
        vector_count = self._pinecone_manager.get_vector_count()
        documents = None
        
        if vector_count == 0:
            print("⚠️ Vector store is empty. Loading documents...")
            documents = process_documents(
                settings.data_path,
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap
            )
        
        # 5. Setup vector store
        self._vector_store = self._pinecone_manager.setup_vector_store(
            embedding=self._embedding_model,
            documents=documents
        )
        
        # 6. Initialize LLM
        self._llm_model = LLMConfig.setup_gemini(
            api_key=settings.gemini_api_key,
            model_name=settings.gemini_model
        )
        
        # 7. Create query engine
        retriever = self._vector_store.as_retriever(search_kwargs={"k": settings.top_k_results})
        self._query_engine = QueryEngine(
            llm_model=self._llm_model,
            retriever=retriever
        )
        
        self._initialized = True
        print("✅ Medical Chatbot Service initialized successfully!\n")
    
    def query(self, question: str, top_k: int = 3, return_sources: bool = False):
        """
        Query the chatbot with a question.
        
        Args:
            question: User's question
            top_k: Number of documents to retrieve
            return_sources: Whether to return source documents
            
        Returns:
            Answer string or dict with answer and sources
        """
        if not self._initialized:
            self.initialize()
        
        # Update retriever's k value if different from default
        if top_k != settings.top_k_results:
            self._query_engine.retriever = self._vector_store.as_retriever(
                search_kwargs={"k": top_k}
            )
        
        result = self._query_engine.query(
            question=question,
            top_k=top_k,
            return_sources=return_sources
        )
        
        return result
    
    def get_vector_count(self) -> int:
        """
        Get the number of vectors in the database.
        
        Returns:
            Number of vectors
        """
        if not self._initialized:
            self.initialize()
        
        return self._pinecone_manager.get_vector_count()
    
    def is_ready(self) -> bool:
        """
        Check if the chatbot service is ready.
        
        Returns:
            True if initialized and ready, False otherwise
        """
        return self._initialized


# Global chatbot service instance (singleton)
chatbot_service = ChatbotService()
