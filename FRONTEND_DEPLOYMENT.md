# 🎨 Frontend Deployment Guide

## Deploy Your DeFi Dashboard to Production

**Timeline: 15-20 minutes**

---

## Option 1: Vercel (Recommended) ⚡

### Why Vercel?
- ✅ 100% Free for personal projects
- ✅ Automatic HTTPS
- ✅ Automatic deployments from Git
- ✅ Built-in CDN
- ✅ Zero configuration for Vite/React

---

## 📋 Prerequisites

- [ ] GCP backend running (from previous setup)
- [ ] Your GCP External IP noted (e.g., `34.123.45.67`)
- [ ] GitHub account
- [ ] Code pushed to GitHub

---

## 🚀 Step-by-Step Deployment

### Step 1: Update Frontend Configuration (5 min)

**On your local machine:**

1. Create production environment file:

```bash
# Navigate to frontend directory
cd frontend

# Create .env.production file
```

2. Add this content to `frontend/.env.production`:

```bash
# Replace with YOUR GCP External IP
VITE_API_BASE_URL=http://YOUR_GCP_IP:8000
```

**Example:**
```bash
VITE_API_BASE_URL=http://34.123.45.67:8000
```

3. **Commit and push:**

```bash
git add .env.production
git commit -m "Add production environment config"
git push origin main
```

---

### Step 2: Deploy to Vercel (5 min)

1. **Go to [vercel.com](https://vercel.com)**
2. Click **"Sign up"** or **"Login"** (use GitHub)
3. Click **"Add New Project"**
4. Click **"Import Git Repository"**
5. Select your repository: `main-project`
6. Configure project:

```
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

7. **Environment Variables:**
   - Click "Add Environment Variable"
   - Key: `VITE_API_BASE_URL`
   - Value: `http://YOUR_GCP_IP:8000` (use your actual IP)
   - Click "Add"

8. Click **"Deploy"**

9. **Wait 2-3 minutes** for deployment

10. **Your dashboard is live!** 🎉
    - URL: `https://your-project.vercel.app`

---

### Step 3: Test Your Live Dashboard (5 min)

1. Open your Vercel URL in browser
2. You should see the dashboard loading
3. Check all tabs:
   - [ ] Protocol Heatmap loads
   - [ ] Risk Analysis shows charts
   - [ ] ML Models displays metrics
   - [ ] Portfolio Analyzer works
   - [ ] Alerts tab functional

**If data doesn't load:**
- Open browser console (F12)
- Check for CORS errors
- See troubleshooting section below

---

## Option 2: Netlify 🌐

### Deploy to Netlify

1. **Go to [netlify.com](https://netlify.com)**
2. Click **"Sign up"** (use GitHub)
3. Click **"Add new site"** → **"Import an existing project"**
4. Select **GitHub**
5. Choose your repository
6. Configure:

```
Base directory: frontend
Build command: npm run build
Publish directory: frontend/dist
```

7. **Environment Variables:**
   - Click "Advanced build settings"
   - Click "New variable"
   - Key: `VITE_API_BASE_URL`
   - Value: `http://YOUR_GCP_IP:8000`

8. Click **"Deploy site"**

9. **Your URL**: `https://your-site.netlify.app`

---

## 🔧 Enable CORS on Backend

**Your backend needs to allow requests from your frontend domain!**

### Step 1: Update Backend CORS Settings

SSH into your GCP instance:

```bash
gcloud compute ssh defi-backend --zone=us-central1-a
```

### Step 2: Update main.py

```bash
cd ~/defi-project/backend
nano app/main.py
```

Find the CORS middleware section and update:

```python
from fastapi.middleware.cors import CORSMiddleware

# Update allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local development
        "http://localhost:3000",
        "https://your-project.vercel.app",  # Add your Vercel URL
        "https://*.vercel.app",  # Allow all Vercel preview URLs
        "https://your-site.netlify.app",  # Or Netlify URL
        "*",  # Or use "*" for all (less secure but simpler)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Quick fix (allow all):**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 3: Restart Backend

```bash
sudo systemctl restart defi-backend

# Check it restarted successfully
sudo systemctl status defi-backend
```

### Step 4: Test Again

Refresh your Vercel/Netlify site - data should now load!

---

## ✅ Deployment Checklist

- [ ] Backend running on GCP
- [ ] `.env.production` created with correct GCP IP
- [ ] Code pushed to GitHub
- [ ] Vercel/Netlify account created
- [ ] Project deployed
- [ ] Environment variables set
- [ ] CORS enabled on backend
- [ ] Dashboard loads successfully
- [ ] All tabs display data
- [ ] No console errors

---

## 🎨 Add AI Assistant to Frontend

### Update Frontend to Include LLM Chat

We'll add a chat interface to your dashboard!

1. **Create chat component** (I'll provide the code)
2. **Add new tab** to dashboard
3. **Connect to LLM API**

**I'll create this for you in the next step!**

---

## 📊 Your Complete Live System

After deployment:

```
┌─────────────────────────┐
│   Users (Anywhere)      │
│                         │
└────────┬────────────────┘
         │
         ↓ HTTPS
┌─────────────────────────┐
│   Vercel/Netlify        │
│   (Frontend Dashboard)  │
│   - React + TypeScript  │
│   - Material-UI         │
│   - Charts & Analytics  │
└────────┬────────────────┘
         │
         ↓ HTTP API
┌─────────────────────────┐
│   Google Cloud (GCP)    │
│   e2-medium Instance    │
│                         │
│   ┌─────────────────┐   │
│   │  FastAPI        │   │
│   │  PostgreSQL     │   │
│   │  TinyLlama      │   │
│   │  Vector Store   │   │
│   └─────────────────┘   │
└─────────────────────────┘
```

---

## 🆘 Troubleshooting

### Dashboard shows empty/no data

**Check 1: Backend is running**
```bash
curl http://YOUR_GCP_IP:8000/api/v1/health
```

**Check 2: CORS is enabled**
- Open browser console (F12)
- Look for CORS errors
- Update backend CORS settings

**Check 3: API URL is correct**
- In Vercel: Settings → Environment Variables
- Should be: `http://YOUR_GCP_IP:8000` (no trailing slash)

### "Failed to fetch" errors

**Enable CORS** (see section above)

### Charts not displaying

**Check data is present:**
```bash
curl http://YOUR_GCP_IP:8000/protocols
```

**Verify vector store is initialized:**
```bash
curl http://YOUR_GCP_IP:8000/api/v1/llm/health
```

### Vercel build fails

**Common issues:**
1. Wrong root directory (should be `frontend`)
2. Missing dependencies - check `package.json`
3. TypeScript errors - fix them locally first

**View build logs:**
- Vercel dashboard → Your project → Deployments → Click latest
- See detailed error messages

---

## 🚀 Automatic Updates

**Vercel/Netlify auto-deploy when you push to GitHub!**

```bash
# Make changes to frontend
cd frontend
# ... edit files ...

# Commit and push
git add .
git commit -m "Update dashboard styling"
git push origin main

# Vercel/Netlify automatically rebuilds and deploys!
# Takes 2-3 minutes
```

---

## 🎯 Next Steps

1. **✅ Deploy frontend** (follow steps above)
2. **🤖 Add AI Assistant chat** (next guide)
3. **🔒 Enable HTTPS** (use Cloudflare - free)
4. **🌐 Add custom domain** (optional)
5. **📊 Add monitoring** (Vercel Analytics - free)

---

## 📝 Save Your URLs

**Backend (GCP):**
- API: `http://YOUR_GCP_IP:8000`
- Docs: `http://YOUR_GCP_IP:8000/docs`
- Health: `http://YOUR_GCP_IP:8000/api/v1/health`

**Frontend (Vercel/Netlify):**
- Dashboard: `https://your-project.vercel.app`
- Settings: Dashboard → Project → Settings

**GitHub:**
- Repository: `https://github.com/YOUR_USERNAME/main-project`

---

## 💰 Cost Summary

| Service | Cost | Free Tier |
|---------|------|-----------|
| **GCP e2-medium** | ~$24/month | Uses $300 credit |
| **Vercel** | $0/month | ✅ Free forever |
| **Domain (optional)** | $10-12/year | ❌ Not free |
| **HTTPS** | $0/month | ✅ Free (auto) |
| **Total** | **~$24/month** | **12 months free with credit** |

---

## ✅ Success Criteria

Your deployment is successful when:

- [ ] Dashboard loads at Vercel/Netlify URL
- [ ] Protocol cards display with risk scores
- [ ] Charts render with historical data
- [ ] ML metrics show model performance
- [ ] Portfolio analyzer accepts input
- [ ] No console errors
- [ ] Data refreshes automatically every 30 seconds
- [ ] Mobile responsive (test on phone)

---

**Ready to deploy? Start with Step 1!** 🚀

