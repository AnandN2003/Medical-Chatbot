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

# Temporarily comment out problematic routes for debugging
try:
    app.include_router(
        auth.router,
        prefix="/api/v1",
        tags=["Authentication"]
    )
    print("✅ Auth router loaded")
except Exception as e:
    print(f"⚠️  Auth router failed to load: {e}")

try:
    app.include_router(
        documents.router,
        prefix="/api/v1",
        tags=["Documents"]
    )
    print("✅ Documents router loaded")
except Exception as e:
    print(f"⚠️  Documents router failed to load: {e}")

try:
    app.include_router(
        chat.router,
        prefix="/api/v1/chat",
        tags=["Chat"]
    )
    print("✅ Chat router loaded")
except Exception as e:
    print(f"⚠️  Chat router failed to load: {e}")


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
    Wrapped in try-except to never crash the app.
    """
    try:
        # Connect to MongoDB with retry logic
        print("="*60)
        print("🔌 ATTEMPTING MONGODB CONNECTION...")
        print("="*60)
        try:
            await connect_to_mongodb()
            print("="*60)
            print("✅ MONGODB CONNECTION SUCCESSFUL!")
            print("="*60 + "\n")
        except Exception as e:
            print("="*60)
            print("❌ MONGODB CONNECTION FAILED!")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)[:500]}")
            print("="*60)
            import traceback
            print("Full Traceback:")
            print(traceback.format_exc())
            print("="*60 + "\n")
            print("⚠️  Application will continue but database features will be limited\n")
        
        # Initialize chatbot service - SKIP FOR NOW to prevent crashes
        print("🔧 Chatbot service will initialize on first query (lazy loading)...")
        print("✅ Startup complete! App is ready.\n")
    except Exception as e:
        print(f"⚠️  Background initialization error: {str(e)}")
        print("⚠️  App will continue to run\n")


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler - FAST startup to bind port quickly.
    Heavy initialization happens in background.
    """
    try:
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
        
        # Run background initialization - with extensive error logging
        asyncio.create_task(initialize_services())
    except Exception as e:
        print(f"⚠️  Startup error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        # Don't raise - let app continue


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
