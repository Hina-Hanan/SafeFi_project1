# 🚀 Complete 2-Hour Deployment Guide

## From Zero to Production with AI Assistant

**What you'll have:**
- ✅ Backend on GCP with TinyLlama
- ✅ Frontend on Vercel with AI chat
- ✅ Complete dashboard with all features
- ✅ 100% Free (uses your $300 GCP credit)

**Total Time: ~2 hours**

---

## 📋 Prerequisites Checklist

- [ ] Google Cloud account with $300 free credit
- [ ] Vercel account (sign up free at vercel.com)
- [ ] GitHub account
- [ ] Your code pushed to GitHub repository
- [ ] 2 hours of focused time

---

## Part 1: Backend Setup on GCP (60 min)

### Step 1.1: Clean Local Machine (5 min)

**From your local computer (Windows PowerShell):**

```powershell
# Stop Ollama if running
taskkill /F /IM ollama.exe

# Remove Mistral (frees 4.1GB)
ollama rm mistral
ollama rm nomic-embed-text

# Verify
ollama list
# Should show empty or only other models
```

✅ **Done!** Freed ~5GB space.

---

### Step 1.2: Create GCP Instance (15 min)

1. **Go to**: [console.cloud.google.com](https://console.cloud.google.com)

2. **Create Project:**
   - Click "Select a project" → "New Project"
   - Name: `defi-risk-assessment`
   - Click "Create"
   - Wait 1-2 minutes

3. **Enable Compute Engine:**
   - Search: "Compute Engine"
   - Click "Enable API"
   - Wait 1 minute

4. **Create VM Instance:**
   - Go to: **Compute Engine** → **VM Instances**
   - Click **"Create Instance"**
   - Configure:
     ```
     Name: defi-backend
     Region: us-central1 (Iowa)
     Zone: us-central1-a
     
     Machine Configuration:
       Series: E2
       Machine type: e2-medium (2 vCPU, 4GB RAM)
     
     Boot Disk:
       OS: Ubuntu 22.04 LTS
       Type: Standard persistent disk
       Size: 30 GB
     
     Firewall:
       ✅ Allow HTTP traffic
       ✅ Allow HTTPS traffic
     ```
   - Click **"Create"**
   - Wait 1-2 minutes

5. **Create Firewall Rule:**
   - Go to: **VPC Network** → **Firewall** → **Create Firewall Rule**
   - Configure:
     ```
     Name: allow-backend-8000
     Network: default
     Direction: Ingress
     Action: Allow
     Targets: All instances
     Source IP: 0.0.0.0/0
     Protocols: TCP → 8000
     ```
   - Click **"Create"**

6. **Note Your External IP:**
   - Go back to **VM Instances**
   - Find your instance
   - **Copy External IP** (e.g., `34.123.45.67`)
   - **SAVE THIS!** You'll need it multiple times.

---

### Step 1.3: Automated Backend Installation (40 min)

**SSH into your instance:**

**Option A: Browser SSH (Easiest)**
1. In VM Instances page
2. Click **"SSH"** button next to your instance
3. Browser window opens with terminal

**Option B: gcloud CLI**
```bash
gcloud compute ssh defi-backend --zone=us-central1-a
```

---

**Run automated setup script:**

```bash
# Update system first
sudo apt update

# Install curl if needed
sudo apt install -y curl

# Download setup script
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/backend/deploy/gcp_tinyllama_setup.sh

# Make executable
chmod +x gcp_tinyllama_setup.sh

# Run it (takes 30-40 minutes)
./gcp_tinyllama_setup.sh
```

**What to enter when prompted:**
- GitHub repo URL: `https://github.com/YOUR_USERNAME/YOUR_REPO.git`
- If private repo: You'll need a Personal Access Token
  - Go to: GitHub → Settings → Developer Settings → Personal Access Tokens
  - Generate new token with `repo` scope
  - Use as password when cloning

**The script will:**
- [1/12] Update system ✅
- [2/12] Install Python 3.11 ✅
- [3/12] Install PostgreSQL ✅
- [4/12] Configure database (saves password to `~/db_password.txt`) ✅
- [5/12] Clone your repository ✅
- [6/12] Setup Python environment ✅
- [7/12] Install Ollama ✅
- [8/12] Pull TinyLlama (1.1GB download) ✅
- [9/12] Pull embedding model ✅
- [10/12] Configure Ollama service ✅
- [11/12] Configure backend environment ✅
- [12/12] Setup backend service ✅

**⏳ Wait for "Setup Complete!" message**

---

### Step 1.4: Initialize Vector Store (10 min)

**Still in SSH terminal:**

```bash
# Initialize RAG embeddings from your database
curl -X POST http://localhost:8000/api/v1/llm/initialize

# This takes 5-10 minutes depending on data size
# You'll see progress updates

# Expected output:
# {
#   "initialized": true,
#   "document_count": 45,
#   "message": "Vector store initialized successfully"
# }
```

**Wait for completion before proceeding.**

---

### Step 1.5: Test Backend (5 min)

**Test locally on GCP:**

```bash
# Test health
curl http://localhost:8000/api/v1/health

# Should return:
# {"status":"ok","database_connected":true,...}

# Test LLM
curl http://localhost:8000/api/v1/llm/health

# Should return:
# {"ollama_available":true,"vector_store_initialized":true,...}

# Test query
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What protocols are monitored?"}'

# Should return a JSON response with "answer" field
```

**✅ If all tests pass, backend is ready!**

---

## Part 2: Frontend Setup (40 min)

### Step 2.1: Update Frontend Configuration (5 min)

**On your local machine:**

```bash
# Navigate to frontend
cd frontend

# Edit .env.production file (already created)
# Open in any text editor
```

**Update `.env.production`:**

```bash
# Replace YOUR_GCP_IP with your actual External IP
VITE_API_BASE_URL=http://34.123.45.67:8000
```

**Save the file.**

---

### Step 2.2: Commit and Push (2 min)

```bash
# Add changes
git add .

# Commit
git commit -m "Add AI Assistant and production config"

# Push to GitHub
git push origin main
```

---

### Step 2.3: Deploy to Vercel (15 min)

1. **Go to**: [vercel.com](https://vercel.com)

2. **Sign up / Login:**
   - Click "Sign up"
   - Choose "Continue with GitHub"
   - Authorize Vercel

3. **Import Project:**
   - Click "Add New Project"
   - Click "Import Git Repository"
   - Select your repository: `main-project`
   - Click "Import"

4. **Configure Build:**
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

5. **Environment Variables:**
   - Click "Environment Variables"
   - Add variable:
     - **Key**: `VITE_API_BASE_URL`
     - **Value**: `http://YOUR_GCP_IP:8000` (use your actual IP!)
   - Click "Add"

6. **Deploy:**
   - Click **"Deploy"**
   - Wait 2-3 minutes
   - You'll see build logs

7. **Success!**
   - You'll get a URL like: `https://your-project.vercel.app`
   - Click "Visit" to see your dashboard

---

### Step 2.4: Enable CORS on Backend (10 min)

**Your frontend needs permission to call the backend!**

**SSH back into GCP:**

```bash
gcloud compute ssh defi-backend --zone=us-central1-a
```

**Edit main.py:**

```bash
cd ~/defi-project/backend
nano app/main.py
```

**Find the CORS section and update:**

```python
from fastapi.middleware.cors import CORSMiddleware

# Add after: app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local dev
        "https://your-project.vercel.app",  # Your Vercel URL
        "https://*.vercel.app",  # All Vercel preview URLs
        "*",  # Or use "*" to allow all (simpler)
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
    allow_origins=["*"],  # Allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Save and exit:**
- Press `Ctrl+X`
- Press `Y`
- Press `Enter`

**Restart backend:**

```bash
sudo systemctl restart defi-backend

# Verify it restarted
sudo systemctl status defi-backend
```

---

### Step 2.5: Test Live Dashboard (8 min)

1. **Open your Vercel URL** in browser

2. **Check all tabs:**
   - [ ] 🔥 Risk Heatmap - Shows protocol cards
   - [ ] 📊 7-Day Analysis - Shows trend charts
   - [ ] 💼 Portfolio - Analyzer works
   - [ ] 🤖 AI Assistant - NEW! Chat interface

3. **Test AI Assistant:**
   - Click "🤖 AI Assistant" tab
   - Should show "ONLINE" status
   - Type: "What are the high-risk protocols?"
   - Click Send
   - Should get a response!

4. **Check browser console:**
   - Press `F12`
   - Go to "Console" tab
   - Should see no errors
   - If CORS errors, double-check CORS setup

---

## Part 3: Final Testing (20 min)

### Test Everything Works

**Use test script from your local machine:**

```bash
# Download test script
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/backend/deploy/test_gcp_deployment.sh

# Make executable
chmod +x test_gcp_deployment.sh

# Run test
./test_gcp_deployment.sh

# Enter your GCP External IP when prompted
```

**Expected output:**
```
✅ Backend is running
✅ Database connected
✅ Ollama is running
✅ Vector store initialized
✅ LLM query successful
✅ Protocols endpoint working
✅ API docs accessible
✅ All critical tests passed!
```

---

## ✅ Complete Success Checklist

### Backend (GCP)
- [ ] GCP instance created (e2-medium)
- [ ] Setup script completed successfully
- [ ] Backend service is active
- [ ] Ollama service is active
- [ ] Database is connected
- [ ] Vector store initialized
- [ ] LLM queries work locally
- [ ] API accessible from internet

### Frontend (Vercel)
- [ ] .env.production configured with GCP IP
- [ ] Code pushed to GitHub
- [ ] Vercel project deployed
- [ ] Environment variables set
- [ ] Dashboard loads successfully
- [ ] All tabs display data
- [ ] AI Assistant tab works
- [ ] Chat sends and receives messages

### Integration
- [ ] CORS configured on backend
- [ ] Frontend calls backend successfully
- [ ] No console errors
- [ ] Protocol data loads
- [ ] Charts render
- [ ] AI responses received

---

## 🎉 You're Live!

### Your URLs

**Backend:**
- API: `http://YOUR_GCP_IP:8000`
- Docs: `http://YOUR_GCP_IP:8000/docs`
- Health: `http://YOUR_GCP_IP:8000/api/v1/health`
- LLM: `http://YOUR_GCP_IP:8000/api/v1/llm/health`

**Frontend:**
- Dashboard: `https://your-project.vercel.app`

---

## 🎯 Try Your AI Assistant!

**Example questions:**
- "What are the high-risk protocols?"
- "Show me Aave's current risk score"
- "What factors contribute to protocol risk?"
- "Which protocols have TVL above $1B?"
- "Explain the ML risk scoring model"
- "What's the average risk score across all protocols?"

---

## 📊 System Architecture

```
┌──────────────────────┐
│   Users (Anywhere)   │
└─────────┬────────────┘
          │ HTTPS
          ↓
┌──────────────────────┐
│   Vercel CDN         │
│   Frontend           │
│   - React Dashboard  │
│   - AI Chat UI       │
│   - Charts/Analytics │
└─────────┬────────────┘
          │ HTTP API
          ↓
┌──────────────────────┐
│   Google Cloud (GCP) │
│   e2-medium          │
│   ┌────────────────┐ │
│   │ FastAPI        │ │
│   │ PostgreSQL     │ │
│   │ TinyLlama      │ │
│   │ RAG/Vector DB  │ │
│   └────────────────┘ │
└──────────────────────┘
```

---

## 💰 Monthly Cost

| Component | Cost | Status |
|-----------|------|--------|
| GCP e2-medium | ~$24/mo | Covered by $300 credit |
| Vercel | $0/mo | Free forever |
| **Total** | **$0/mo** | **12 months free** |

---

## 🔧 Management Commands

### View Logs

**Backend:**
```bash
# SSH into GCP
gcloud compute ssh defi-backend --zone=us-central1-a

# View backend logs
sudo journalctl -u defi-backend -f

# View Ollama logs
sudo journalctl -u ollama -f
```

**Frontend:**
- Vercel Dashboard → Your Project → Deployments → View Logs

### Restart Services

**Backend:**
```bash
# Restart backend
sudo systemctl restart defi-backend

# Restart Ollama
sudo systemctl restart ollama

# Restart both
sudo systemctl restart defi-backend ollama
```

### Update Code

**Backend:**
```bash
cd ~/defi-project
git pull
sudo systemctl restart defi-backend
```

**Frontend:**
```bash
# Just push to GitHub - Vercel auto-deploys!
git add .
git commit -m "Update frontend"
git push origin main
```

### Refresh Vector Store

```bash
# After adding new protocols/data
curl -X POST http://YOUR_GCP_IP:8000/api/v1/llm/refresh
```

---

## 🆘 Troubleshooting

### Dashboard shows no data

1. **Check backend health:**
   ```bash
   curl http://YOUR_GCP_IP:8000/api/v1/health
   ```

2. **Check CORS:**
   - Open browser console (F12)
   - Look for CORS errors
   - Update CORS in `app/main.py`

3. **Check environment variable:**
   - Vercel → Settings → Environment Variables
   - Should be: `http://YOUR_GCP_IP:8000`

### AI Assistant shows "OFFLINE"

1. **Check LLM health:**
   ```bash
   curl http://YOUR_GCP_IP:8000/api/v1/llm/health
   ```

2. **Check Ollama:**
   ```bash
   sudo systemctl status ollama
   curl http://localhost:11434
   ```

3. **Check vector store:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/llm/initialize
   ```

### Backend not responding

1. **Check service status:**
   ```bash
   sudo systemctl status defi-backend
   ```

2. **View logs:**
   ```bash
   sudo journalctl -u defi-backend -n 50
   ```

3. **Restart:**
   ```bash
   sudo systemctl restart defi-backend
   ```

### Vercel build fails

1. **Check build logs** in Vercel dashboard
2. **Common fixes:**
   - Wrong root directory (should be `frontend`)
   - TypeScript errors (fix locally first)
   - Missing dependencies (check `package.json`)

---

## 🎯 Next Steps

1. **✅ Everything deployed and working**
2. **🔒 Enable HTTPS** (optional):
   - Use Cloudflare (free)
   - Or upgrade backend to use Load Balancer
3. **🌐 Add custom domain** (optional):
   - Buy domain ($10-12/year)
   - Point to Vercel
4. **📊 Add monitoring**:
   - GCP Cloud Monitoring (free tier)
   - Vercel Analytics (free)
5. **🚀 Upgrade model** (if needed):
   - Switch to e2-standard-2 (8GB RAM)
   - Install Mistral or Llama3

---

## 📚 Documentation Files

- **This guide**: `COMPLETE_DEPLOYMENT_GUIDE.md`
- **Checklist**: `LLM_SETUP_CHECKLIST.md`
- **Backend setup**: `GCP_TINYLLAMA_SETUP.md`
- **Frontend deployment**: `FRONTEND_DEPLOYMENT.md`
- **Cleanup guide**: `CLEANUP_LOCAL.md`

---

## ✨ Features You Now Have

✅ **Real-time DeFi protocol monitoring**
✅ **ML-powered risk scoring**
✅ **Interactive risk heatmaps**
✅ **Historical trend analysis**
✅ **Portfolio risk analyzer**
✅ **Custom risk alerts**
✅ **AI-powered chat assistant**
✅ **RAG-based context retrieval**
✅ **Production-ready deployment**
✅ **Auto-scaling & auto-restart**
✅ **Mobile-responsive UI**

---

**Total Time: ~2 hours**
**Total Cost: $0/month for 12 months**
**Result: Production-ready DeFi risk assessment platform with AI!** 🎉

---

**Questions? Issues? Check troubleshooting section or review logs!**

