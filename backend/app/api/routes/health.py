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
    Fast endpoint - does not trigger initialization.
    
    Returns:
        HealthResponse with API status and version
    """
    vector_count = None
    
    # Only get vector count if service is already initialized
    # Do NOT initialize here - that's done on startup
    # Use try-except with timeout to avoid hanging
    if chatbot_service.is_ready():
        try:
            # Quick vector count retrieval
            vector_count = chatbot_service.get_vector_count()
        except Exception as e:
            print(f"⚠️ Warning: Could not get vector count in health check: {e}")
            # Return None instead of failing - health check should be fast
            vector_count = None
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        vector_count=vector_count
    )


@router.get("/ready")
async def readiness_check():
    """
    Readiness check to verify chatbot is initialized.
    Fast check without heavy operations.
    
    Returns:
        Dict with ready status
    """
    is_ready = chatbot_service.is_ready()
    
    return {
        "ready": is_ready,
        "message": "Chatbot is ready" if is_ready else "Chatbot is initializing...",
        "status": "ready" if is_ready else "initializing"
    }


@router.get("/status")
async def detailed_status():
    """
    Detailed status check including vector count.
    This may be slower as it queries Pinecone.
    
    Returns:
        Dict with detailed status information
    """
    is_ready = chatbot_service.is_ready()
    vector_count = None
    
    if is_ready:
        try:
            vector_count = chatbot_service.get_vector_count()
        except Exception as e:
            print(f"⚠️ Error getting vector count: {e}")
    
    return {
        "ready": is_ready,
        "vector_count": vector_count,
        "version": settings.app_version,
        "status": "ready" if is_ready else "initializing"
    }
