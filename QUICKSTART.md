# 🚀 Quick Start Guide - MongoDB Integration & Document Upload

## Prerequisites

- Python 3.8+
- Node.js 18+
- MongoDB Atlas account (free tier works)
- Google Gemini API key
- Pinecone API key

## ⚡ Quick Setup (5 minutes)

### 1. MongoDB Atlas Setup (2 minutes)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up/Login and create a **FREE M0 cluster**
3. Create database user:
   - Go to Database Access → Add New User
   - Username: `medchatbot`
   - Password: Generate secure password
   - Database User Privileges: `Atlas admin` or `Read and write to any database`
4. Whitelist IP:
   - Go to Network Access → Add IP Address
   - For development: Click "Allow Access from Anywhere" (0.0.0.0/0)
5. Get connection string:
   - Go to Database → Connect → Connect your application
   - Copy connection string
   - Replace `<password>` with your password
   - Add database name: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/medical_chatbot?retryWrites=true&w=majority`

### 2. Backend Setup (2 minutes)

```powershell
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env

# Edit .env file and add:
# - MONGODB_URI (from step 1)
# - JWT_SECRET_KEY (generate: python -c "import secrets; print(secrets.token_urlsafe(32))")
# - GEMINI_API_KEY (your existing key)
# - PINECONE_API_KEY (your existing key)

# Start backend
python -m uvicorn app.main:app --reload
```

### 3. Frontend Setup (1 minute)

```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start frontend
npm run dev
```

## 🎯 Test the Application

### 1. Sign Up
1. Open browser: `http://localhost:5173`
2. Click "Get Started"
3. In the modal, go to "Sign Up" side
4. Fill in:
   - Full Name: `Test User`
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `Test1234` (must have uppercase, lowercase, digit)
   - Confirm Password: `Test1234`
5. Click "Sign Up"
6. You'll be redirected to Document Upload page

### 2. Upload a Document
1. Click "Choose a file..."
2. Select a PDF, DOCX, or TXT file (max 50MB)
3. Fill in:
   - Document Title: `Medical Textbook`
   - Category: `Anatomy` (or any category)
   - Tags: `anatomy, medical` (optional)
4. Click "Upload Document"
5. Wait for processing to complete

### 3. Chat with Your Documents
1. Once document shows "Processed" status
2. Click "Continue to Chat →"
3. Ask questions about your document
4. Get AI-powered answers with source citations

## 📝 Environment Variables Reference

### Required Variables

```env
# MongoDB (from Atlas)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/medical_chatbot

# JWT (generate new)
JWT_SECRET_KEY=your-32-char-secret-here

# API Keys (existing)
GEMINI_API_KEY=your-gemini-key
PINECONE_API_KEY=your-pinecone-key
```

### Optional Variables (with defaults)

```env
# Database name
MONGODB_DB_NAME=medical_chatbot

# JWT settings
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# File upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=pdf,docx,xlsx,txt,doc,xls

# Server
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 🔍 Verify Everything Works

### Check Backend
- Open: `http://localhost:8000/docs`
- You should see FastAPI Swagger UI with endpoints:
  - `/api/v1/auth/signup`
  - `/api/v1/auth/login`
  - `/api/v1/documents/upload`
  - etc.

### Check MongoDB
- Log into MongoDB Atlas
- Go to Database → Browse Collections
- You should see:
  - `medical_chatbot` database
  - Collections: `users`, `documents`
  - Your test user in `users` collection

### Check Frontend
- Open: `http://localhost:5173`
- Landing page loads
- Auth modal opens
- Can sign up/login
- Document upload page works

## 🐛 Common Issues

### MongoDB Connection Failed
```
Error: Failed to connect to MongoDB
```
**Fix:**
- Check MONGODB_URI is correct
- Verify IP is whitelisted (0.0.0.0/0 for dev)
- Ensure database user has correct permissions
- Test connection using MongoDB Compass

### JWT Token Issues
```
Error: Could not validate credentials
```
**Fix:**
- Ensure JWT_SECRET_KEY is set in `.env`
- Must be at least 32 characters
- Regenerate token by logging in again

### File Upload Fails
```
Error: File type not allowed
```
**Fix:**
- Check file extension is in ALLOWED_EXTENSIONS
- Verify file size < MAX_FILE_SIZE_MB
- Ensure `uploads/` directory exists

### CORS Errors
```
Access to fetch blocked by CORS policy
```
**Fix:**
- Check CORS_ORIGINS includes `http://localhost:5173`
- Restart backend server
- Clear browser cache

## 📊 API Testing with Swagger

1. Open: `http://localhost:8000/docs`

2. **Test Signup:**
   - Expand `POST /api/v1/auth/signup`
   - Click "Try it out"
   - Fill in JSON:
     ```json
     {
       "email": "test@example.com",
       "username": "testuser",
       "full_name": "Test User",
       "password": "Test1234"
     }
     ```
   - Click "Execute"
   - Copy `access_token` from response

3. **Test Upload:**
   - Expand `POST /api/v1/documents/upload`
   - Click "Try it out"
   - Click "Authorize" (lock icon at top)
   - Paste token: `Bearer <your_token>`
   - Upload file
   - Check response

4. **Test Get Documents:**
   - Expand `GET /api/v1/documents/`
   - Click "Try it out"
   - Click "Execute"
   - See your uploaded documents

## 🎓 Next Steps

1. **Secure Your App:**
   - Change JWT_SECRET_KEY to a strong random value
   - Restrict MongoDB IP whitelist in production
   - Enable HTTPS

2. **Customize:**
   - Add more document categories
   - Customize UI colors/theme
   - Add more file formats

3. **Deploy:**
   - Deploy backend to Heroku/Railway/Render
   - Deploy frontend to Vercel/Netlify
   - Use production MongoDB cluster

## 📚 Additional Resources

- **Full Guide:** `IMPLEMENTATION_GUIDE.md`
- **MongoDB Setup:** `MONGODB_SETUP.md`
- **API Documentation:** `http://localhost:8000/docs`
- **Redoc:** `http://localhost:8000/redoc`

## ✅ Success Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Connection string obtained
- [ ] Backend `.env` configured
- [ ] Backend dependencies installed
- [ ] Backend server running
- [ ] Frontend dependencies installed
- [ ] Frontend server running
- [ ] Can sign up new user
- [ ] Can login existing user
- [ ] Can upload document
- [ ] Document processing works
- [ ] Can view documents
- [ ] Can delete document
- [ ] Can chat with documents

---

**You're all set! 🎉**

If you encounter any issues, check the detailed `IMPLEMENTATION_GUIDE.md` or refer to error logs in the terminal.
