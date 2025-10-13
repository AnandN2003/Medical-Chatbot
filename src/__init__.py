"""
Medical Chatbot Package
Modular RAG-based medical question-answering system.
"""

# Import main components for easy access
from src.data_loader import load_pdf_files, filter_to_minimal_docs, split_documents, process_documents
from src.embeddings import get_embedding_model, get_embedding_dimension
from src.vector_store import PineconeManager
from src.llm_config import LLMConfig
from src.query_engine import QueryEngine

__all__ = [
    'load_pdf_files',
    'filter_to_minimal_docs',
    'split_documents',
    'process_documents',
    'get_embedding_model',
    'get_embedding_dimension',
    'PineconeManager',
    'LLMConfig',
    'QueryEngine',
]
