"""
Configuration Module
Handles application settings and environment variables.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    app_name: str = "Medical Chatbot API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API Keys
    pinecone_api_key: str
    gemini_api_key: str
    openai_api_key: Optional[str] = None
    
    # Pinecone Configuration
    pinecone_index_name: str = "medical-chatbot"
    pinecone_dimension: int = 384
    pinecone_metric: str = "cosine"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
    
    # Embedding Model Configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # LLM Configuration
    gemini_model: str = "models/gemini-2.5-flash"
    
    # Document Processing
    chunk_size: int = 500
    chunk_overlap: int = 20
    
    # Data Path
    data_path: str = str(Path(__file__).parent.parent.parent / "data")
    
    # CORS Settings
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # Query Settings
    top_k_results: int = 3
    
    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
