# 🚀 Medical Chatbot - Production Deployment Guide

## Overview

This guide covers deploying your Medical Chatbot to production:
- **Frontend**: Vercel (with custom .tech domain)
- **Backend**: Render
- **Database**: MongoDB Atlas
- **Vector DB**: Pinecone

---

## 📦 Pre-Deployment Checklist

### ✅ Before You Start:

- [ ] GitHub repository is up to date
- [ ] MongoDB connection string is from MongoDB Atlas (cloud)
- [ ] Pinecone API key is for production index
- [ ] Gemini API key is active
- [ ] All secrets are stored securely (never commit .env files)

---

## 🎨 Part 1: Deploy Backend to Render

### Step 1: Create Render Account

1. Go to https://render.com
2. Sign up with your GitHub account
3. Verify your email

### Step 2: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `AnandN2003/Medical-Chatbot`
3. Configure the service:

**Basic Settings**:
- **Name**: `medical-chatbot-backend`
- **Region**: Choose closest to your users (e.g., Oregon, Frankfurt)
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`

**Build & Deploy**:
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

**Instance Type**:
- **Free** (for testing) or **Starter** ($7/month for production)

### Step 3: Add Environment Variables

In Render dashboard, go to **Environment** tab and add:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/medical_chatbot?retryWrites=true&w=majority
MONGODB_DB_NAME=medical_chatbot
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
PINECONE_API_KEY=your-pinecone-api-key
GEMINI_API_KEY=your-gemini-api-key
PINECONE_INDEX_NAME=medical-chatbot
PINECONE_DIMENSION=384
PINECONE_METRIC=cosine
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
GEMINI_MODEL=models/gemini-2.5-flash
CHUNK_SIZE=500
CHUNK_OVERLAP=20
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=pdf,docx,xlsx,txt,doc,xls
CORS_ORIGINS=https://yourdomain.tech,https://www.yourdomain.tech
TOP_K_RESULTS=3
```

**Important**:
- Replace `your-pinecone-api-key` with your actual key
- Replace `your-gemini-api-key` with your actual key
- Generate a new strong JWT secret: `openssl rand -hex 32`
- Update `CORS_ORIGINS` with your Vercel domain (we'll add this after frontend deployment)

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Once deployed, you'll get a URL like: `https://medical-chatbot-backend.onrender.com`

### Step 5: Test Backend

Visit: `https://medical-chatbot-backend.onrender.com/docs`

You should see the FastAPI Swagger documentation.

---

## 🌐 Part 2: Deploy Frontend to Vercel

### Step 1: Prepare Frontend for Deployment

First, we need to update the API URL in your frontend to use environment variables.

**Create a `.env` file in the frontend folder**:

```env
VITE_API_URL=https://medical-chatbot-backend.onrender.com
```

**Update all API calls in your frontend to use the env variable**:

We'll need to replace all instances of `http://localhost:8000` with the environment variable.

### Step 2: Create Vercel Account

1. Go to https://vercel.com
2. Sign up with your GitHub account
3. Verify your email

### Step 3: Deploy to Vercel

**Option A: Via Vercel Dashboard**:

1. Click **"Add New Project"**
2. Import your GitHub repository: `AnandN2003/Medical-Chatbot`
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

4. **Environment Variables** (in Vercel dashboard):
   ```
   VITE_API_URL=https://medical-chatbot-backend.onrender.com
   ```

5. Click **"Deploy"**

**Option B: Via Vercel CLI** (Faster):

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend folder
cd frontend

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

### Step 4: Get Your Vercel URL

After deployment, you'll get a URL like:
- `https://medical-chatbot-xyz123.vercel.app`

---

## 🌍 Part 3: Connect .tech Domain

### Step 1: Purchase .tech Domain

1. Go to https://get.tech or any domain registrar (Namecheap, GoDaddy, etc.)
2. Search for your desired domain (e.g., `medichatbot.tech`)
3. Purchase the domain (~$10-15/year)

### Step 2: Add Domain to Vercel

1. In Vercel dashboard, go to your project
2. Click **"Settings"** → **"Domains"**
3. Add your custom domain: `medichatbot.tech`
4. Vercel will show you DNS records to add

### Step 3: Configure DNS

In your domain registrar (get.tech), add these DNS records:

**For Root Domain** (`medichatbot.tech`):
```
Type: A
Name: @
Value: 76.76.21.21 (Vercel's IP)
TTL: 3600
```

**For www Subdomain** (`www.medichatbot.tech`):
```
Type: CNAME
Name: www
Value: cname.vercel-dns.com
TTL: 3600
```

**Note**: Vercel will show you the exact records in the dashboard.

### Step 4: Wait for DNS Propagation

- DNS changes can take 5 minutes to 48 hours
- Usually propagates within 1-2 hours
- Check status: https://www.whatsmydns.net

### Step 5: Enable SSL

Vercel automatically provisions SSL certificates via Let's Encrypt. Once DNS propagates:
- Your site will be available at `https://medichatbot.tech`
- Auto-redirects HTTP to HTTPS

---

## 🔧 Part 4: Update CORS Settings

Once your frontend domain is live, update backend CORS:

**In Render Dashboard** → Your Backend Service → **Environment**:

Update `CORS_ORIGINS`:
```env
CORS_ORIGINS=https://medichatbot.tech,https://www.medichatbot.tech,https://medical-chatbot-xyz123.vercel.app
```

Save and redeploy the backend.

---

## 🗂️ Part 5: MongoDB Atlas Setup (If Not Already Cloud)

### If using local MongoDB, migrate to Atlas:

1. Go to https://www.mongodb.com/cloud/atlas
2. Create free cluster (M0)
3. Create database user
4. Whitelist IP: `0.0.0.0/0` (allow all - for Render)
5. Get connection string
6. Update `MONGODB_URI` in Render environment variables

---

## 📊 Part 6: Monitor & Optimize

### Render Monitoring:
- Check logs: Render Dashboard → Logs
- Monitor uptime
- Upgrade to paid plan if needed

### Vercel Monitoring:
- Analytics: Vercel Dashboard → Analytics
- View deployment logs
- Check build times

### Performance Tips:
- Enable Vercel Edge Network (automatic)
- Use Render's CDN for static assets
- Monitor MongoDB connection pool
- Optimize Pinecone queries

---

## 🔐 Security Checklist

- [ ] JWT secret is strong and unique
- [ ] All API keys are in environment variables
- [ ] CORS is configured correctly
- [ ] MongoDB has authentication enabled
- [ ] Rate limiting is enabled (add if needed)
- [ ] HTTPS is enforced everywhere
- [ ] .env files are in .gitignore

---

## 🐛 Troubleshooting

### Backend not responding:
- Check Render logs
- Verify environment variables
- Test with `/health` endpoint

### Frontend API errors:
- Check browser console
- Verify CORS settings
- Check `VITE_API_URL` in Vercel

### Domain not resolving:
- Wait for DNS propagation
- Check DNS records with `nslookup medichatbot.tech`
- Verify Vercel domain settings

### 502 Bad Gateway on Render:
- Check if service is running
- Verify start command
- Check memory usage (upgrade if needed)

---

## 💰 Estimated Monthly Costs

| Service | Plan | Cost |
|---------|------|------|
| Vercel | Hobby | **Free** |
| Render | Free Tier | **Free** |
| MongoDB Atlas | M0 Free | **Free** |
| Pinecone | Starter | **Free** (up to limits) |
| .tech Domain | Annual | **~$15/year** |
| **Total** | | **$1.25/month** |

**For Production** (recommended):
| Service | Plan | Cost |
|---------|------|------|
| Vercel | Pro | **$20/month** |
| Render | Starter | **$7/month** |
| MongoDB Atlas | M10 | **$10/month** |
| Pinecone | Standard | **$70/month** |
| .tech Domain | Annual | **~$15/year** |
| **Total** | | **~$108/month** |

---

## 🎉 Success Checklist

After deployment, test:

- [ ] Frontend loads at `https://medichatbot.tech`
- [ ] Landing page works
- [ ] Main page renders correctly
- [ ] Auth (Login/Signup) works
- [ ] Free chat works (without login)
- [ ] Document upload works (with login)
- [ ] Chat with uploaded docs works
- [ ] All animations and UI elements work
- [ ] Mobile responsive
- [ ] HTTPS is enabled
- [ ] Backend API is accessible

---

## 📞 Support

- **Vercel Docs**: https://vercel.com/docs
- **Render Docs**: https://render.com/docs
- **Vercel Discord**: https://vercel.com/discord
- **Render Community**: https://community.render.com

---

## 🔄 Continuous Deployment

Both Vercel and Render auto-deploy on git push:

```bash
# Make changes
git add .
git commit -m "feat: new feature"
git push origin main

# Vercel & Render will auto-deploy! 🚀
```

---

**Last Updated**: October 21, 2025  
**Version**: 1.0 - Production Ready
