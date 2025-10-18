# Troubleshooting: "Load Data" Error

## Error Message
```
Uncaught (in promise) Error: A listener indicated an asynchronous response by returning true, 
but the message channel closed before a response was received
```

## What This Error Means

This error is **NOT** caused by your application code. It's a warning from browser extensions (typically Chrome DevTools, React DevTools, or other extensions) that are trying to intercept network requests or messages.

## Solutions

### Solution 1: Ignore the Error (Recommended)
This error **does not affect your application functionality**. It's just a warning in the console. If your "Load Data" button works correctly and loads the medical_book.pdf, you can safely ignore this message.

### Solution 2: Disable Browser Extensions
If the error is bothersome:

1. Open Chrome DevTools (F12)
2. Go to Extensions (chrome://extensions/)
3. Temporarily disable extensions one by one to identify the culprit
4. Common culprits:
   - React Developer Tools
   - Redux DevTools
   - Grammarly
   - LastPass
   - Any security or privacy extensions

### Solution 3: Test in Incognito Mode
1. Open your browser in Incognito/Private mode
2. Navigate to `http://localhost:5173` (or your Vite dev server port)
3. Test the "Load Data" functionality
4. If it works without the error, it confirms a browser extension is the cause

## How to Verify Load Data Works

Even with the error message, check if the data loading is successful:

### 1. Check Backend Status
The backend should show these logs when you click "Load Data":
```
INFO:     127.0.0.1:PORT - "POST /api/v1/chat/query HTTP/1.1" 200 OK
```

### 2. Check Frontend Status
After clicking "Load Data", you should see:
- Button changes from "Load Data" to "✓ Loaded" with green background
- Status message shows: "✅ Medical_book.pdf loaded successfully!"
- Chat input becomes enabled
- You can type and send messages

### 3. Test a Query
Try asking a question like:
- "What is diabetes?"
- "Tell me about heart disease"
- "What are the symptoms of flu?"

If you get a response, **the data is loaded successfully** regardless of the console error.

## Backend Not Running?

If clicking "Load Data" doesn't work at all, check if your backend is running:

### Check Backend Server
```powershell
# In terminal, navigate to backend folder
cd backend

# Activate virtual environment (if not already active)
# For Windows:
..\medibot_env\Scripts\Activate.ps1

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Verify Backend is Running
Open browser and go to:
```
http://localhost:8000/api/v1/health
```

You should see:
```json
{
  "status": "healthy",
  "vector_count": 0  // or some number if data is loaded
}
```

### Check Backend API Documentation
```
http://localhost:8000/docs
```

This shows all available API endpoints.

## Code Improvements Made

### 1. Better Error Handling
- Added try-catch blocks for all API calls
- Prevented multiple simultaneous load attempts
- More descriptive error messages

### 2. Improved Status Display
- Shows loading status in real-time
- Visual feedback for success/error states
- Status text appears next to Load Data button

### 3. Authenticated vs Free User Logic
- Authenticated users: Data is automatically considered loaded (uses their uploaded documents)
- Free users: Must click "Load Data" to initialize medical_book.pdf

## Testing Checklist

- [ ] Backend server is running on port 8000
- [ ] Frontend dev server is running on port 5173
- [ ] Can access http://localhost:8000/api/v1/health
- [ ] Click "Load Data" button
- [ ] Button changes to "✓ Loaded"
- [ ] Input field becomes enabled
- [ ] Can send a test query
- [ ] Receive a response from the AI

## Still Having Issues?

### Check Browser Console for Real Errors
Look for errors that are NOT the "listener indicated asynchronous response" message:
- Network errors (failed to fetch)
- CORS errors
- 404 or 500 status codes

### Check Backend Logs
Look for actual errors in the backend terminal:
- Import errors
- File not found errors
- Database connection errors

### Verify File Paths
Make sure `medical_book.pdf` exists in your data folder:
```
Medical-Chatbot/
  └── data/
      └── medical_book.pdf  ← Should exist here
```

## Summary

**The "listener indicated asynchronous response" error is a browser extension warning and can be safely ignored.** 

Focus on whether the actual functionality works:
1. ✅ Backend responds to requests
2. ✅ Data loads successfully
3. ✅ Chat queries return answers

If all three work, your application is functioning correctly!
