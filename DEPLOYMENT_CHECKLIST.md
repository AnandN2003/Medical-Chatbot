# 🚀 Quick Deployment Checklist

## Pre-Deployment
- [ ] All code is committed and pushed to GitHub
- [ ] MongoDB Atlas connection string ready
- [ ] Pinecone API key ready
- [ ] Gemini API key ready
- [ ] Strong JWT secret generated (`openssl rand -hex 32`)

## Step 1: Deploy Backend (Render)
- [ ] Create account at https://render.com
- [ ] Connect GitHub repository
- [ ] Create new Web Service
- [ ] Set root directory to `backend`
- [ ] Add all environment variables
- [ ] Deploy and get backend URL (e.g., https://medical-chatbot-backend.onrender.com)
- [ ] Test: Visit `https://your-backend.onrender.com/docs`

## Step 2: Deploy Frontend (Vercel)
- [ ] Create account at https://vercel.com
- [ ] Connect GitHub repository
- [ ] Set root directory to `frontend`
- [ ] Set framework preset to `Vite`
- [ ] Add environment variable: `VITE_API_URL=https://your-backend.onrender.com`
- [ ] Deploy and get Vercel URL (e.g., https://medical-chatbot-xyz.vercel.app)
- [ ] Test: Visit your Vercel URL

## Step 3: Update CORS
- [ ] Go to Render dashboard
- [ ] Update `CORS_ORIGINS` environment variable with your Vercel URL
- [ ] Redeploy backend

## Step 4: Connect .tech Domain
- [ ] Purchase domain from https://get.tech
- [ ] Add domain in Vercel → Settings → Domains
- [ ] Copy DNS records from Vercel
- [ ] Add DNS records in your domain registrar
- [ ] Wait for DNS propagation (1-24 hours)
- [ ] Verify HTTPS is working

## Step 5: Final Update
- [ ] Update `CORS_ORIGINS` in Render with your `.tech` domain
- [ ] Update `VITE_API_URL` in Vercel with your `.tech` domain (if using custom backend domain)
- [ ] Test all features:
  - [ ] Landing page loads
  - [ ] Login/Signup works
  - [ ] Free chat works
  - [ ] Document upload works
  - [ ] Chat with docs works

## 🎉 Done!

Your app is live at:
- **Frontend**: https://yourdomain.tech
- **Backend**: https://your-backend.onrender.com

---

## Estimated Time
- Backend deployment: 10 minutes
- Frontend deployment: 5 minutes
- Domain setup: 1-24 hours (DNS propagation)
- **Total**: ~2-24 hours

---

## Need Help?
See full guide: `DEPLOYMENT_GUIDE.md`
