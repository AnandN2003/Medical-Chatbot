"""
Medical Chatbot API - Main Application
FastAPI backend for the medical chatbot with RAG capabilities.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health, chat, auth, documents
from app.config import settings
from app.core.database import connect_to_mongodb, close_mongodb_connection

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Medical Chatbot API with RAG (Retrieval-Augmented Generation) using Google Gemini",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"]
)

app.include_router(
    auth.router,
    prefix="/api/v1",
    tags=["Authentication"]
)

app.include_router(
    documents.router,
    prefix="/api/v1",
    tags=["Documents"]
)

app.include_router(
    chat.router,
    prefix="/api/v1/chat",
    tags=["Chat"]
)


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        Dict with API welcome message and available endpoints
    """
    return {
        "message": "🩺 Medical Chatbot API",
        "version": settings.app_version,
        "docs": "/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "chat": "/api/v1/chat/query"
        }
    }


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    Run any initialization code here.
    """
    print("\n" + "="*60)
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print("="*60)
    print(f"📝 API Docs: http://localhost:8000/docs")
    print(f"🔍 Health Check: http://localhost:8000/api/v1/health")
    print(f"🔐 Auth Endpoints: http://localhost:8000/api/v1/auth/")
    print(f"📄 Documents: http://localhost:8000/api/v1/documents/")
    print(f"💬 Chat Endpoint: http://localhost:8000/api/v1/chat/query")
    print("="*60 + "\n")
    
    # Connect to MongoDB with retry logic
    print("🔌 Connecting to MongoDB...")
    try:
        await connect_to_mongodb()
        print("✅ MongoDB connected!\n")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {str(e)[:100]}")
        print("⚠️  Application will start but database features will be limited\n")
        # Don't raise - allow app to start even if MongoDB fails
    
    # Initialize chatbot service on startup
    print("🔧 Initializing chatbot service...")
    try:
        from app.services import chatbot_service
        chatbot_service.initialize()
        print("✅ Chatbot service ready!\n")
    except Exception as e:
        print(f"⚠️  Chatbot initialization warning: {str(e)[:100]}\n")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler.
    Clean up resources here.
    """
    print("\n👋 Shutting down Medical Chatbot API...")
    await close_mongodb_connection()
    print("✅ MongoDB connection closed")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload during development
    )
