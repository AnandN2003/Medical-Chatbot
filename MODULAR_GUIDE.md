# Medical Chatbot - Modular Structure

## 📁 Project Structure

```
Medical-Chatbot/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── data_loader.py           # PDF loading & document processing
│   ├── embeddings.py            # Embedding model configuration
│   ├── vector_store.py          # Pinecone vector database operations
│   ├── llm_config.py            # LLM (Gemini) configuration
│   ├── query_engine.py          # RAG query processing
│   ├── store_index.py           # Script to create/update vector index
│   ├── run_chatbot.py           # Main chatbot runner
│   ├── helper.py                # Legacy helper functions
│   └── prompt.py                # Prompt templates
├── research/
│   ├── trials.ipynb             # Experimental notebook
│   ├── medical_chatbot_rag.py   # Original monolithic script
│   └── medical_chatbot_pipeline.py  # Pipeline version
├── data/                        # PDF documents for RAG
├── .env                         # API keys (not in git)
└── requirements.txt             # Dependencies

```

## 🚀 Quick Start

### 1. First Time Setup - Store Index

Before using the chatbot, you need to process documents and create the vector index:

```bash
cd "d:\anand\Medical Chatbot\Medical-Chatbot"
python src/store_index.py
```

This will:
- Load all PDFs from the `data/` folder
- Split them into chunks
- Create embeddings
- Store them in Pinecone

### 2. Run the Chatbot

After creating the index, run the interactive chatbot:

```bash
python src/run_chatbot.py
```

Or use it programmatically:

```python
from src.run_chatbot import run_chatbot

# Non-interactive mode (single test query)
run_chatbot(interactive=False)

# Interactive mode
run_chatbot(interactive=True)
```

## 📚 Module Documentation

### `data_loader.py`
Handles PDF loading and text processing.

**Functions:**
- `load_pdf_files(data_path)` - Load PDFs from directory
- `filter_to_minimal_docs(docs)` - Clean document metadata
- `split_documents(documents, chunk_size, chunk_overlap)` - Split into chunks
- `process_documents(data_path)` - Complete processing pipeline

**Example:**
```python
from src.data_loader import process_documents

chunks = process_documents("data/", chunk_size=500, chunk_overlap=20)
print(f"Created {len(chunks)} chunks")
```

### `embeddings.py`
Manages embedding model configuration.

**Functions:**
- `get_embedding_model(model_name)` - Initialize HuggingFace embeddings
- `get_embedding_dimension(model_name)` - Get embedding vector dimension

**Example:**
```python
from src.embeddings import get_embedding_model

embedding = get_embedding_model("sentence-transformers/all-MiniLM-L6-v2")
```

### `vector_store.py`
Complete Pinecone vector database management.

**Class: `PineconeManager`**

**Methods:**
- `create_index(dimension, metric, cloud, region)` - Create new index
- `get_index()` - Get index object
- `get_index_stats()` - Get index statistics
- `get_vector_count()` - Count vectors in index
- `setup_vector_store(embedding, documents)` - Setup/load vector store
- `add_documents(vector_store, documents)` - Add new documents
- `delete_index()` - Delete the index
- `list_indexes()` - List all indexes

**Example:**
```python
from src.vector_store import PineconeManager
from src.embeddings import get_embedding_model

# Initialize
pm = PineconeManager(api_key="your-key", index_name="medical-chatbot")

# Create index
pm.create_index(dimension=384)

# Setup vector store
embedding = get_embedding_model()
vector_store = pm.setup_vector_store(embedding)

# Get stats
print(f"Vectors: {pm.get_vector_count()}")
```

### `llm_config.py`
LLM model configuration.

**Class: `LLMConfig`**

**Static Methods:**
- `setup_gemini(api_key, model_name)` - Initialize Gemini model
- `list_available_models(api_key)` - List available Gemini models
- `get_model_info(api_key, model_name)` - Get model information

**Example:**
```python
from src.llm_config import LLMConfig

# Setup Gemini
model = LLMConfig.setup_gemini(api_key="your-key", model_name="models/gemini-2.5-flash")

# List models
models = LLMConfig.list_available_models(api_key="your-key")
print(models)
```

### `query_engine.py`
RAG query processing engine.

**Class: `QueryEngine`**

**Methods:**
- `create_prompt(question, context)` - Format prompt
- `retrieve_context(question, top_k)` - Get relevant documents
- `generate_response(prompt)` - Generate answer
- `query(question, top_k, return_sources)` - Complete RAG query
- `interactive_query()` - Start interactive session

**Example:**
```python
from src.query_engine import QueryEngine

# Initialize
query_engine = QueryEngine(llm_model, retriever)

# Simple query
answer = query_engine.query("What is diabetes?")
print(answer)

# Query with sources
result = query_engine.query("What is diabetes?", return_sources=True)
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")

# Interactive mode
query_engine.interactive_query()
```

## 🔧 Standalone Scripts

### `store_index.py`
Create and populate the Pinecone vector database.

```bash
python src/store_index.py
```

**What it does:**
1. Loads PDFs from `data/` folder
2. Processes and chunks documents
3. Creates embeddings
4. Stores in Pinecone
5. Shows statistics

### `run_chatbot.py`
Run the medical chatbot.

```bash
# Interactive mode
python src/run_chatbot.py

# Or import and use
from src.run_chatbot import run_chatbot
run_chatbot(interactive=True)
```

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
PINECONE_API_KEY=your_pinecone_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_API_KEY=your_gemini_api_key_here
```

## 📝 Usage Examples

### Example 1: Complete Setup from Scratch

```python
import os
from dotenv import load_dotenv
from src.data_loader import process_documents
from src.embeddings import get_embedding_model, get_embedding_dimension
from src.vector_store import PineconeManager
from src.llm_config import LLMConfig
from src.query_engine import QueryEngine

# Load environment
load_dotenv()

# Process documents
chunks = process_documents("data/")

# Setup embeddings
embedding = get_embedding_model()
dim = get_embedding_dimension()

# Setup Pinecone
pm = PineconeManager(os.getenv("PINECONE_API_KEY"))
pm.create_index(dimension=dim)
vector_store = pm.setup_vector_store(embedding, chunks)

# Create retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# Setup LLM
llm = LLMConfig.setup_gemini(os.getenv("GEMINI_API_KEY"))

# Create query engine
qe = QueryEngine(llm, retriever)

# Query
answer = qe.query("What is acromegaly?")
print(answer)
```

### Example 2: Query Existing Index

```python
import os
from dotenv import load_dotenv
from src.embeddings import get_embedding_model
from src.vector_store import PineconeManager
from src.llm_config import LLMConfig
from src.query_engine import QueryEngine

load_dotenv()

# Load existing index
embedding = get_embedding_model()
pm = PineconeManager(os.getenv("PINECONE_API_KEY"))
vector_store = pm.setup_vector_store(embedding)

# Setup retriever and LLM
retriever = vector_store.as_retriever(search_kwargs={"k": 3})
llm = LLMConfig.setup_gemini(os.getenv("GEMINI_API_KEY"))

# Query
qe = QueryEngine(llm, retriever)
result = qe.query("What causes diabetes?", return_sources=True)

print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
```

## 🎯 Benefits of Modular Structure

1. **Separation of Concerns** - Each module has a single responsibility
2. **Reusability** - Import and use components independently
3. **Testing** - Test each module separately
4. **Maintainability** - Easy to update or replace components
5. **Scalability** - Add new features without touching existing code
6. **Clean Code** - Better organization and readability

## 🔄 Migration from Old Code

The old monolithic script (`medical_chatbot_rag.py`) has been refactored into:

- Document processing → `data_loader.py`
- Embeddings → `embeddings.py`
- Vector storage → `vector_store.py`
- LLM setup → `llm_config.py`
- Query logic → `query_engine.py`
- Main scripts → `store_index.py` & `run_chatbot.py`

All functionality is preserved, just better organized!
