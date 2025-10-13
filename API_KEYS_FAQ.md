# 🔑 API Keys & Vector Database - FAQ

## Q: If I delete the vector database from Pinecone, will my API keys change?

**A: NO! ✅** Your API keys will **remain exactly the same**.

### Why?
- API keys are tied to your **Pinecone account**, not to individual indexes
- Deleting an index only removes the stored vectors (data)
- Your account credentials (API key) stay unchanged

---

## Q: What happens when I delete the index from Pinecone website?

### What Gets Deleted ❌
- All stored vector embeddings
- Document chunks in the index
- The index itself (database structure)

### What Stays the Same ✅
- Your Pinecone API key
- Your Gemini API key  
- Your account quota and limits
- All other indexes (if you have any)

---

## Q: After deleting the index, how do I recreate it?

### **Method 1: Run `store_index.py` (Recommended)**

```bash
# Step 1: Delete index from Pinecone website
# (Your API key stays the same!)

# Step 2: Create fresh index with all documents
python src/store_index.py
```

**What it does:**
1. ✅ Creates new `medical-chatbot` index in Pinecone
2. ✅ Loads all PDFs from `data/` folder
3. ✅ Processes and chunks documents
4. ✅ Creates embeddings
5. ✅ Stores everything in Pinecone

---

### **Method 2: Run `run_chatbot.py` (New Auto-Create Feature)**

```bash
# Just run the chatbot!
python src/run_chatbot.py
```

**What it does NOW (updated):**
1. ✅ Checks if index exists → creates it if missing
2. ✅ Checks if index is empty → processes documents if needed
3. ✅ Automatically populates the index with your PDFs
4. ✅ Starts the chatbot

**Parameters:**
```python
run_chatbot(
    index_name="medical-chatbot",
    auto_create_index=True  # Set to False to skip auto-creation
)
```

---

## 📊 Comparison

### Before Update:
```
Delete index → ❌ run_chatbot.py fails
              ↓
         Need to manually run store_index.py first
```

### After Update (NOW):
```
Delete index → ✅ run_chatbot.py auto-creates it
              ↓
         Automatically processes PDFs and populates index
              ↓
         Chatbot ready to use!
```

---

## 🔄 Complete Workflow Examples

### Scenario 1: Fresh Start (No Index Exists)

```bash
# Just run the chatbot - it handles everything!
python src/run_chatbot.py
```

**Output:**
```
🩺 MEDICAL CHATBOT
============================================================

🔑 API Key Status:
   PINECONE_API_KEY: ✅ Found
   GEMINI_API_KEY: ✅ Found

============================================================
Loading Embedding Model
============================================================
🤖 Loading embedding model...
   Embedding model loaded successfully

============================================================
Connecting to Vector Database
============================================================
📌 Setting up Pinecone index: medical-chatbot...
   Creating new index with dimension=384

💾 Setting up vector store...
   📊 Current vectors in index: 0

⚠️ Index is empty. Processing documents from 'data/' folder...
============================================================
📚 Loading PDF files from data...
   Loaded 637 documents
🔧 Filtering documents...
   Filtered 637 documents
✂️ Splitting documents into chunks...
   Created 5859 chunks
============================================================
✅ Added 5859 document chunks to the index

🔍 Creating retriever...
   ✅ Retriever ready

[... chatbot starts ...]
```

---

### Scenario 2: Deleted Index, Want to Recreate

```bash
# Option A: Use dedicated script (faster, cleaner)
python src/store_index.py

# Option B: Just run chatbot (auto-creates)
python src/run_chatbot.py
```

Both work! Choose based on your preference.

---

### Scenario 3: Index Already Exists with Data

```bash
# Just run normally - skips document processing
python src/run_chatbot.py
```

**Output:**
```
============================================================
Connecting to Vector Database
============================================================
📌 Setting up Pinecone index: medical-chatbot...
   Index 'medical-chatbot' already exists

💾 Setting up vector store...
   📊 Current vectors in index: 16720
   ✅ Loading existing index...

[... starts chatbot immediately ...]
```

---

## 🎯 Key Takeaways

1. **API Keys Never Change** ✅
   - Delete/create indexes as many times as you want
   - Same API keys work forever (unless you regenerate them manually)

2. **Two Ways to Create Index:**
   - `store_index.py` - Dedicated indexing script
   - `run_chatbot.py` - Now auto-creates if missing (NEW!)

3. **Smart Detection:**
   - Automatically checks if index exists
   - Automatically populates if empty
   - Skips processing if data already exists

4. **No Manual Steps Needed:**
   - Old: Delete → run store_index → run chatbot
   - New: Delete → run chatbot (handles everything!)

---

## 🛠️ Advanced: Disable Auto-Create

If you want the old behavior (fail if index missing):

```python
from src.run_chatbot import run_chatbot

# Disable auto-creation
run_chatbot(auto_create_index=False)
```

This will error if the index doesn't exist, forcing you to run `store_index.py` first.

---

## ✨ Summary

**Your Question:** "Will API keys be same if I delete the database?"

**Answer:** 
- ✅ YES, API keys stay the same
- ✅ You can delete and recreate indexes freely
- ✅ Now `run_chatbot.py` auto-creates index if missing
- ✅ No manual steps needed anymore!

Just run `python src/run_chatbot.py` and it handles everything! 🎉
