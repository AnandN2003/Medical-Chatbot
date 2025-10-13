"""
Health Check Routes
"""

from fastapi import APIRouter
from app.models import HealthResponse
from app.services import chatbot_service
from app.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify API is running.
    
    Returns:
        HealthResponse with API status and version
    """
    vector_count = None
    
    # Try to get vector count if service is initialized
    if chatbot_service.is_ready():
        try:
            vector_count = chatbot_service.get_vector_count()
        except Exception:
            pass  # Ignore errors in health check
    else:
        # Service not initialized yet - initialize it now
        try:
            chatbot_service.initialize()
            vector_count = chatbot_service.get_vector_count()
        except Exception as e:
            # If initialization fails, still return healthy status
            # but log the error
            print(f"Warning: Could not initialize chatbot service: {e}")
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        vector_count=vector_count
    )


@router.get("/ready")
async def readiness_check():
    """
    Readiness check to verify chatbot is initialized.
    
    Returns:
        Dict with ready status
    """
    is_ready = chatbot_service.is_ready()
    
    return {
        "ready": is_ready,
        "message": "Chatbot is ready" if is_ready else "Chatbot is initializing..."
    }
