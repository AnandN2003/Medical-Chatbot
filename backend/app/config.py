"""
Configuration Module
Handles application settings and environment variables.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    app_name: str = "Medical Chatbot API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # MongoDB Configuration
    mongodb_uri: str
    mongodb_db_name: str = "medical_chatbot"
    
    # JWT Configuration
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
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
    
    # File Upload Configuration
    upload_dir: str = "uploads"
    max_file_size_mb: int = 50
    allowed_extensions: str = "pdf,docx,xlsx,txt,doc,xls"
    
    # Data Path
    data_path: str = str(Path(__file__).parent.parent.parent / "data")
    
    # CORS Settings
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Query Settings
    top_k_results: int = 3
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins
    
    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get list of allowed file extensions."""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    def get_upload_path(self, user_id: str) -> Path:
        """Get upload directory path for a specific user."""
        path = Path(self.upload_dir) / user_id
        path.mkdir(parents=True, exist_ok=True)
        return path


# Global settings instance
settings = Settings()
