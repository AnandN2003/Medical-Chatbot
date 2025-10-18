# How to Start the Backend Server (Using Base Conda Environment)

## Prerequisites

You need to install the backend dependencies in your base conda environment.

## Step 1: Install Required Packages

Open a **NEW** PowerShell terminal and run:

```powershell
# Navigate to the backend folder
cd "d:\anand\Medical Chatbot\Medical-Chatbot\backend"

# Install all required packages
pip install -r requirements.txt
```

This will install:
- FastAPI
- Uvicorn
- MongoDB drivers
- LangChain
- Google Gemini
- And all other dependencies

**Note**: Installation may take 5-10 minutes depending on your internet speed.

## Step 2: Start the Backend Server

After installation completes, start the server:

```powershell
# Make sure you're in the backend folder
cd "d:\anand\Medical Chatbot\Medical-Chatbot\backend"

# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Alternative**: You can also use the batch file:
```powershell
.\start.bat
```

## Step 3: Verify Backend is Running

You should see output like:
```
============================================================
🚀 Starting Medical Chatbot API v1.0.0
============================================================
📝 API Docs: http://localhost:8000/docs
🔍 Health Check: http://localhost:8000/api/v1/health
🔐 Auth Endpoints: http://localhost:8000/api/v1/auth/
📄 Documents: http://localhost:8000/api/v1/documents/
💬 Chat Endpoint: http://localhost:8000/api/v1/chat/query
============================================================

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Step 4: Test the Backend

Open your browser and go to:

### API Documentation
```
http://localhost:8000/docs
```
This shows all available API endpoints with interactive documentation.

### Health Check
```
http://localhost:8000/api/v1/health
```
Should return:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-14T...",
  "vector_count": 0
}
```

### Root Endpoint
```
http://localhost:8000/
```
Should return:
```json
{
  "message": "🩺 Medical Chatbot API",
  "version": "1.0.0",
  "docs": "/docs",
  "endpoints": {
    "health": "/api/v1/health",
    "chat": "/api/v1/chat/query"
  }
}
```

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'fastapi'"
**Solution**: Run `pip install -r requirements.txt` first

### Error: "ModuleNotFoundError: No module named 'uvicorn'"
**Solution**: Run `pip install uvicorn[standard]`

### Error: MongoDB Connection Failed
**Solution**: 
1. Make sure MongoDB is installed and running
2. Check your `.env` file has correct MongoDB connection string
3. Default: `mongodb://localhost:27017/medical_chatbot`

### Error: "No module named 'google.generativeai'"
**Solution**: Run `pip install google-generativeai`

### Error: Port 8000 already in use
**Solution**: 
1. Find and kill the process using port 8000:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```
2. Or use a different port:
```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Error: API Keys Missing
**Solution**:
1. Create a `.env` file in the backend folder
2. Add your API keys:
```env
# Google Gemini API Key
GOOGLE_API_KEY=your_gemini_api_key_here

# Pinecone API Key (if using)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENV=your_pinecone_environment

# MongoDB
MONGODB_URL=mongodb://localhost:27017/medical_chatbot

# JWT Secret
SECRET_KEY=your-secret-key-here
```

## Quick Start Commands (Copy-Paste)

### Terminal 1 - Backend Server
```powershell
cd "d:\anand\Medical Chatbot\Medical-Chatbot\backend"
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend Dev Server (if needed)
```powershell
cd "d:\anand\Medical Chatbot\Medical-Chatbot\frontend"
npm run dev
```

## Expected Terminal Windows

You should have **2 terminals running**:

1. **Backend Terminal**: Running `uvicorn` on port 8000
2. **Frontend Terminal**: Running `vite` dev server on port 5173

Both should remain open while developing!

## Stopping the Server

Press `Ctrl + C` in the backend terminal to stop the server.

## Auto-Reload

The `--reload` flag enables auto-reload. Any changes to Python files will automatically restart the server.

---

**Note**: Keep the backend terminal open and running. Don't close it while using the application!
