"""
Chat Routes
API endpoints for chatbot interactions.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import ChatRequest, ChatResponse
from app.models.schemas import UserInDB
from app.services import chatbot_service
from app.core.auth import get_current_user_optional

router = APIRouter()


@router.post("/query", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def query_chatbot(
    request: ChatRequest,
    current_user: Optional[UserInDB] = Depends(get_current_user_optional)
):
    """
    Query the medical chatbot with a question.
    
    Authentication is optional:
    - With auth: Users query only their own uploaded documents (namespace: user_<id>)
    - Without auth: Users query the default Medical_book.pdf data (default namespace)
    
    Args:
        request: ChatRequest with question and optional parameters
        current_user: Currently authenticated user (optional)
        
    Returns:
        ChatResponse with answer and optional sources
        
    Raises:
        HTTPException: If query processing fails
    """
    try:
        # Initialize service if not already done (lazy loading)
        if not chatbot_service.is_ready():
            chatbot_service.initialize()
        
        # Get user_id if authenticated
        user_id = None
        if current_user:
            user_id = str(current_user.id)
            print(f"💬 User {current_user.username} (ID: {user_id}) asking: {request.question[:50]}...")
        else:
            print(f"💬 Anonymous user asking: {request.question[:50]}...")
        
        # Process the query with optional user_id filter
        result = chatbot_service.query(
            question=request.question,
            user_id=user_id,  # None for free users, user_id for authenticated users
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
        print(f"❌ Error processing query: {str(e)}")
        import traceback
        traceback.print_exc()
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
