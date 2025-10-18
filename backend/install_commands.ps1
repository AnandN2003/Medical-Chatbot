# Install all packages in medibot environment
# Copy and paste these commands one by one into your PowerShell terminal
# Make sure (medibot) is shown in your prompt

# Core packages
pip install fastapi uvicorn[standard] python-dotenv pydantic-settings python-multipart

# MongoDB drivers (includes bson)
pip install pymongo motor

# Authentication
pip install "python-jose[cryptography]" "passlib[bcrypt]" bcrypt email-validator

# LangChain
pip install langchain langchain-community langchain-google-genai langchain-text-splitters

# Embeddings and AI
pip install sentence-transformers google-generativeai

# Vector Database
pip install "pinecone>=5.0.0"

# Document Processing
pip install pypdf python-docx openpyxl

# Utilities
pip install aiofiles httpx
