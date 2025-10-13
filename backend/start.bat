@echo off
echo ============================================================
echo Medical Chatbot Backend - Starting Server
echo ============================================================
echo.

cd /d "d:\anand\Medical Chatbot\Medical-Chatbot\backend"

echo Starting FastAPI server...
echo Server will be available at: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
