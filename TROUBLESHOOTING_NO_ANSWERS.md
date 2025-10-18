# Troubleshooting: Not Getting Answers

## 🔍 Quick Diagnosis

### Symptom: "I'm not getting any answers"

This usually means one of these issues:

1. ❌ Documents marked as "processed" but NOT in Pinecone (the bug we just fixed)
2. ❌ Backend not restarted with the fix
3. ❌ No documents uploaded for your user account
4. ❌ Retriever not finding documents in your namespace

---

## ✅ Step-by-Step Fix

### Step 1: Restart Backend with Fix

```powershell
# In backend terminal
cd backend

# Stop current server (Ctrl+C)

# Start with fix applied
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Watch for startup logs**:
```
🚀 Starting Medical Chatbot API v1.0.0
🔌 Connecting to MongoDB...
✅ MongoDB connected!

🔧 Initializing chatbot service...
📌 Setting up Pinecone index: medical-chatbot...
   Index 'medical-chatbot' already exists
```

---

### Step 2: Check Your Documents

**Click the new "🔄 Refresh" button** (now visible for authenticated users)

**You should see**:
- ✅ "2 document(s) ready" → Documents exist
- ❌ "Upload documents to start chatting" → No documents yet

---

### Step 3: Re-Upload Documents (If Needed)

**If you see "Upload documents to start chatting"**:

1. Go to **Upload page** (Documents section)
2. Upload your PDF again
3. Wait for processing

**Watch backend logs during upload**:
```
🔧 add_documents_to_vectorstore called with 2345 documents, namespace: user_<your_id>

💾 Setting up vector store...
   📊 Current vectors in index (total): 5859
   👤 Using namespace: user_<your_id>
   📤 Uploading 2345 documents to namespace: user_<your_id>
   ✅ Uploaded 2345 documents to namespace

✅ Documents added to namespace: user_<your_id>
```

**Good signs**:
- ✅ "📤 Uploading X documents to namespace"
- ✅ "✅ Uploaded X documents to namespace"

**Bad signs** (means fix not applied):
- ❌ "✅ Loading existing index..." (without "Uploading")
- ❌ No mention of uploading documents

---

### Step 4: Test Query

**Ask a simple question**:
- "what is diabetes?"
- "what medical conditions are discussed?"

**Watch backend logs**:
```
💬 User test1 (ID: <your_id>) asking: what is diabetes?...
🔍 Querying with user namespace: user_<your_id>
   📚 Searching top 3 documents in user namespace
   🔎 Retrieving documents for question: 'what is diabetes?'
   ✅ Retriever returned 3 documents
   📄 Retrieved 3 documents
      1. Current Essentials of Medicine.pdf (user: <your_id>)
         Content length: 500 chars
         Preview: Diabetes is a chronic condition...
   📝 Total context length: 1500 characters
```

**If you see**:
- ✅ "Retrieved 3 documents" → Good! Documents found
- ❌ "Retrieved 0 documents" → Problem! No documents in namespace
- ❌ "⚠️ WARNING: No documents retrieved!" → Critical! Empty namespace

---

## 🐛 Common Issues

### Issue 1: "Retrieved 0 documents"

**Cause**: Documents not actually in Pinecone

**Fix**:
1. Restart backend
2. Re-upload documents
3. Verify upload logs show "📤 Uploading"

---

### Issue 2: "Context is empty"

**Cause**: Documents retrieved but have no content

**Fix**:
1. Check document upload - might be corrupted
2. Try uploading a different PDF
3. Check file size and format

---

### Issue 3: "Upload documents to start chatting"

**Cause**: No documents found for your user

**Fix**:
1. Upload documents via Upload page
2. Wait for "Processing completed" status
3. Click "🔄 Refresh" on Chat page

---

### Issue 4: Can't see "🔄 Refresh" button

**Cause**: Frontend not updated

**Fix**:
1. Restart frontend:
   ```powershell
   cd frontend
   npm run dev
   ```
2. Hard refresh browser (Ctrl+Shift+R)
3. Clear browser cache if needed

---

## 🧪 Debug Checklist

Run through this checklist:

- [ ] Backend restarted with fix
- [ ] Frontend restarted (to show Refresh button)
- [ ] Logged in as the correct user
- [ ] Clicked "🔄 Refresh" button
- [ ] See document count (e.g., "2 document(s) ready")
- [ ] If no documents, uploaded via Upload page
- [ ] Checked backend logs during upload
- [ ] Saw "📤 Uploading X documents to namespace"
- [ ] Saw "✅ Uploaded X documents to namespace"
- [ ] Tried asking a question
- [ ] Checked backend logs during query
- [ ] Saw "Retrieved X documents" (X > 0)
- [ ] Saw document previews in logs
- [ ] Got actual answer (not "I don't know")

---

## 📊 Expected vs Actual

### Expected Flow:
```
1. Login → Auto-check documents
2. See "2 document(s) ready"
3. Ask question
4. Backend: "Retrieved 3 documents"
5. Backend: "Total context length: 1500 chars"
6. Get real answer
```

### If Broken:
```
1. Login → Auto-check documents
2. See "Upload documents to start" ← Documents not in Pinecone
3. Re-upload documents
4. Click "🔄 Refresh"
5. See "2 document(s) ready"
6. Ask question → Now works!
```

---

## 🆘 Still Not Working?

If after all this you still don't get answers:

1. **Share backend terminal output** from:
   - Document upload process
   - Query attempt

2. **Share frontend console** (F12 → Console):
   - Any errors during query?

3. **Check Pinecone dashboard**:
   - Does namespace `user_<your_id>` exist?
   - Does it have vectors?

4. **Try different question**:
   - Instead of "who is the author?"
   - Try: "what medical conditions are discussed?"
   - Medical content more likely throughout book

---

## ✅ Success Indicators

You know it's working when:

1. ✅ "🔄 Refresh" button visible (authenticated users)
2. ✅ Shows "X document(s) ready"
3. ✅ Backend logs: "📤 Uploading X documents"
4. ✅ Backend logs: "Retrieved X documents" (X > 0)
5. ✅ Backend logs: "Total context length: XXX characters"
6. ✅ Get actual answer from your documents
7. ✅ No "I don't know" or "empty context" responses

---

**Follow these steps in order and you should get answers!** 🚀
