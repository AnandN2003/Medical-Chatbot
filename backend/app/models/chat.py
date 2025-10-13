"""
Chat Models
Pydantic models for chat API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    """Request model for chat queries."""
    
    question: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="The user's medical question"
    )
    top_k: Optional[int] = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of relevant documents to retrieve"
    )
    return_sources: Optional[bool] = Field(
        default=False,
        description="Whether to include source documents in the response"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the symptoms of diabetes?",
                "top_k": 3,
                "return_sources": True
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat queries."""
    
    answer: str = Field(
        ...,
        description="The chatbot's answer to the question"
    )
    sources: Optional[List[str]] = Field(
        default=None,
        description="List of source documents used to generate the answer"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Diabetes symptoms include increased thirst, frequent urination, and unexplained weight loss.",
                "sources": ["Medical_book.pdf"]
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")
    vector_count: Optional[int] = Field(None, description="Number of vectors in the database")
