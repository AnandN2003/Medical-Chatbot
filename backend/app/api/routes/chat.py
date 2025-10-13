"""
Chat Routes
API endpoints for chatbot interactions.
"""

from fastapi import APIRouter, HTTPException, status
from app.models import ChatRequest, ChatResponse
from app.services import chatbot_service

router = APIRouter()


@router.post("/query", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def query_chatbot(request: ChatRequest):
    """
    Query the medical chatbot with a question.
    
    Args:
        request: ChatRequest with question and optional parameters
        
    Returns:
        ChatResponse with answer and optional sources
        
    Raises:
        HTTPException: If query processing fails
    """
    try:
        # Initialize service if not already done (lazy loading)
        if not chatbot_service.is_ready():
            chatbot_service.initialize()
        
        # Process the query
        result = chatbot_service.query(
            question=request.question,
            top_k=request.top_k,
            return_sources=request.return_sources
        )
        
        # Format response based on return_sources flag
        if request.return_sources:
            return ChatResponse(
                answer=result['answer'],
                sources=result.get('sources', [])
            )
        else:
            return ChatResponse(
                answer=result if isinstance(result, str) else result.get('answer', ''),
                sources=None
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/")
async def chat_info():
    """
    Get information about the chat endpoint.
    
    Returns:
        Dict with endpoint information
    """
    return {
        "endpoint": "/chat/query",
        "method": "POST",
        "description": "Query the medical chatbot",
        "example_request": {
            "question": "What are the symptoms of diabetes?",
            "top_k": 3,
            "return_sources": True
        }
    }
