"""
Medical Chatbot API - Main Application
FastAPI backend for the medical chatbot with RAG capabilities.
"""

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health, chat, auth, documents
from app.config import settings
from app.core.database import connect_to_mongodb, close_mongodb_connection
import asyncio

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


async def initialize_services():
    """
    Initialize services in the background after the app starts.
    This prevents blocking the port binding.
    """
    # Connect to MongoDB with retry logic
    print("🔌 Connecting to MongoDB in background...")
    try:
        await connect_to_mongodb()
        print("✅ MongoDB connected!\n")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {str(e)[:100]}")
        print("⚠️  Application will continue but database features will be limited\n")
    
    # Initialize chatbot service - SKIP FOR NOW to prevent crashes
    print("🔧 Chatbot service will initialize on first query (lazy loading)...")
    print("✅ Startup complete! App is ready.\n")


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler - FAST startup to bind port quickly.
    Heavy initialization happens in background.
    """
    print("\n" + "="*60)
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print("="*60)
    print(f"📝 API Docs: http://localhost:8000/docs")
    print(f"🔍 Health Check: http://localhost:8000/api/v1/health")
    print(f"🔐 Auth Endpoints: http://localhost:8000/api/v1/auth/")
    print(f"📄 Documents: http://localhost:8000/api/v1/documents/")
    print(f"💬 Chat Endpoint: http://localhost:8000/api/v1/chat/query")
    print("="*60)
    print("⚡ App ready! Port is now open.")
    print("🔄 Background services initializing...\n")
    
    # Run initialization in background to avoid blocking port binding
    asyncio.create_task(initialize_services())


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
