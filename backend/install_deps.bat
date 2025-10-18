@echo off
REM Install all required packages in medibot conda environment

echo ============================================================
echo Installing Medical Chatbot Backend Dependencies
echo Environment: medibot
echo ============================================================
echo.

REM Install core packages
echo [1/8] Installing FastAPI and Uvicorn...
pip install fastapi uvicorn[standard] python-dotenv pydantic-settings python-multipart

echo.
echo [2/8] Installing MongoDB drivers...
pip install pymongo motor

echo.
echo [3/8] Installing Authentication packages...
pip install "python-jose[cryptography]" "passlib[bcrypt]" bcrypt email-validator

echo.
echo [4/8] Installing LangChain packages...
pip install langchain langchain-community langchain-google-genai langchain-text-splitters

echo.
echo [5/8] Installing Embeddings and AI...
pip install sentence-transformers google-generativeai

echo.
echo [6/8] Installing Vector Database...
pip install "pinecone>=5.0.0"

echo.
echo [7/8] Installing Document Processing...
pip install pypdf python-docx openpyxl

echo.
echo [8/8] Installing Utilities...
pip install aiofiles httpx

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo You can now start the backend server with:
echo python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
pause
