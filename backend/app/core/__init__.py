"""
Medical Chatbot - Core Module
Contains all the core chatbot functionality (formerly src/).
"""

from .data_loader import (
    load_pdf_files,
    filter_to_minimal_docs,
    split_documents,
    process_documents
)
from .embeddings import get_embedding_model, get_embedding_dimension
from .vector_store import PineconeManager
from .llm_config import LLMConfig
from .query_engine import QueryEngine

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
