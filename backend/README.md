# 🩺 Medical Chatbot Backend

FastAPI-based backend for the Medical Chatbot with RAG (Retrieval-Augmented Generation) using Google Gemini and Pinecone vector database.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Development](#development)
- [Deployment](#deployment)

---

## ✨ Features

- **🤖 RAG-Powered Responses**: Retrieval-Augmented Generation using Pinecone and Google Gemini
- **⚡ FastAPI Backend**: High-performance async API with automatic documentation
- **🔍 Semantic Search**: Vector similarity search using HuggingFace embeddings
- **📚 Medical Knowledge**: Trained on medical PDF documents
- **🔄 Auto-Initialization**: Automatically creates vector database on first run
- **📊 Health Monitoring**: Built-in health check and readiness endpoints
- **🌐 CORS Support**: Ready for frontend integration

---

## 🏗️ Architecture

```
backend/
├── app/
│   ├── core/               # Core chatbot logic
│   │   ├── data_loader.py  # PDF loading & processing
│   │   ├── embeddings.py   # Embedding model setup
│   │   ├── vector_store.py # Pinecone operations
│   │   ├── llm_config.py   # Gemini LLM setup
│   │   └── query_engine.py # RAG query processing
│   │
│   ├── api/                # API routes
│   │   └── routes/
│   │       ├── chat.py     # Chat endpoints
│   │       └── health.py   # Health check endpoints
│   │
│   ├── services/           # Business logic
│   │   └── chatbot_service.py
│   │
│   ├── models/             # Pydantic models
│   │   └── chat.py
│   │
│   ├── config.py           # Configuration
│   └── main.py             # FastAPI app
│
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- Conda or virtualenv (recommended)
- API Keys:
  - Pinecone API key ([get here](https://www.pinecone.io/))
  - Google Gemini API key ([get here](https://ai.google.dev/))

### 2. Environment Setup

```powershell
# Navigate to backend directory
cd backend

# Create conda environment
conda create -n medibot python=3.10 -y
conda activate medibot

# Or use venv
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```powershell
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
notepad .env
```

Required variables in `.env`:
```env
PINECONE_API_KEY=your_pinecone_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Run the Server

```powershell
# From the backend directory
cd app
python main.py

# Or use uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔌 API Endpoints

### Root
```
GET /
```
Returns API information and available endpoints.

### Health Check
```
GET /api/v1/health
```
**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "vector_count": 16720
}
```

### Readiness Check
```
GET /api/v1/ready
```
Checks if the chatbot service is initialized.

### Chat Query
```
POST /api/v1/chat/query
```

**Request Body:**
```json
{
  "question": "What are the symptoms of diabetes?",
  "top_k": 3,
  "return_sources": true
}
```

**Response:**
```json
{
  "answer": "Diabetes symptoms include increased thirst, frequent urination, and unexplained weight loss.",
  "sources": ["Medical_book.pdf"]
}
```

---

## ⚙️ Configuration

All configuration is handled through environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `PINECONE_API_KEY` | Pinecone API key | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `PINECONE_INDEX_NAME` | Name of Pinecone index | medical-chatbot |
| `EMBEDDING_MODEL` | HuggingFace model name | sentence-transformers/all-MiniLM-L6-v2 |
| `GEMINI_MODEL` | Gemini model version | models/gemini-2.5-flash |
| `CHUNK_SIZE` | Document chunk size | 500 |
| `TOP_K_RESULTS` | Number of retrieval results | 3 |

---

## 🔧 Development

### Project Structure

- **`app/core/`**: Core chatbot logic (moved from `src/`)
- **`app/api/`**: API routes and endpoints
- **`app/services/`**: Business logic layer
- **`app/models/`**: Pydantic request/response models
- **`app/config.py`**: Centralized configuration

### Running in Development Mode

```powershell
# With auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing the API

```powershell
# Using curl
curl -X POST "http://localhost:8000/api/v1/chat/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is diabetes?", "return_sources": true}'

# Using Python requests
python -c "
import requests
response = requests.post('http://localhost:8000/api/v1/chat/query', 
    json={'question': 'What is diabetes?', 'return_sources': True})
print(response.json())
"
```

### API Documentation

FastAPI automatically generates interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🚢 Deployment

### Option 1: Docker (Coming Soon)

```dockerfile
# Dockerfile will be added for containerized deployment
```

### Option 2: Cloud Platforms

**Render / Railway / Heroku:**
1. Connect your GitHub repository
2. Set environment variables in the platform
3. Deploy the `backend` directory
4. Use command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**AWS / Azure / GCP:**
1. Use a managed container service or VM
2. Install dependencies and set environment variables
3. Run with Gunicorn: `gunicorn app.main:app -k uvicorn.workers.UvicornWorker`

---

## 📝 API Usage Examples

### Python Client

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Health check
health = requests.get(f"{BASE_URL}/health").json()
print(f"Status: {health['status']}, Vectors: {health['vector_count']}")

# Query chatbot
response = requests.post(
    f"{BASE_URL}/chat/query",
    json={
        "question": "What causes high blood pressure?",
        "top_k": 3,
        "return_sources": True
    }
).json()

print(f"Answer: {response['answer']}")
print(f"Sources: {response['sources']}")
```

### JavaScript/TypeScript

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';

// Query chatbot
async function askQuestion(question) {
  const response = await fetch(`${BASE_URL}/chat/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: question,
      top_k: 3,
      return_sources: true
    })
  });
  
  const data = await response.json();
  return data;
}

askQuestion('What is hypertension?')
  .then(data => console.log(data));
```

---

## 🆘 Troubleshooting

### Port Already in Use
```powershell
# Change port in command
uvicorn app.main:app --reload --port 8001
```

### Import Errors
```powershell
# Make sure you're in the backend directory
cd backend

# Run from backend directory
python -m app.main
```

### Vector Database Empty
The service will automatically load documents on first run. Check:
1. PDFs exist in `../data/` directory
2. Pinecone API key is correct
3. Check server logs for errors

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [Google Gemini API](https://ai.google.dev/)
- [LangChain Documentation](https://python.langchain.com/)

---

## 📄 License

This project is part of the Medical Chatbot application.

---

**Need help?** Check the main project README or open an issue on GitHub.
