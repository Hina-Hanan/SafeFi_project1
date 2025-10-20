# 🚀 START HERE - Complete Setup in 2 Hours

## What You're Building

A **production-ready DeFi risk assessment platform** with:
- ✅ Backend on GCP (FastAPI + PostgreSQL + TinyLlama)
- ✅ Frontend on Vercel (React dashboard with AI chat)
- ✅ **100% FREE** for 12 months (uses your $300 GCP credit)

---

## ⏱️ Timeline

- **Step 1:** Clean up local (5 min)
- **Step 2:** Setup GCP backend (60 min - mostly automated)
- **Step 3:** Deploy frontend (30 min)
- **Step 4:** Test everything (10 min)

**Total: ~2 hours**

---

## 🎯 Step 1: Clean Up Local (5 min) - DO THIS NOW

**Open PowerShell on your Windows machine:**

```powershell
# Stop Ollama if running
taskkill /F /IM ollama.exe

# Remove Mistral to free space
ollama rm mistral
ollama rm nomic-embed-text

# Verify
ollama list
```

✅ **Done!** You freed ~5GB.

---

## 🎯 Step 2: Setup GCP Backend (60 min)

### 2.1: Create GCP Instance (15 min)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create project: `defi-risk-assessment`
3. Enable "Compute Engine API"
4. Create VM Instance:
   - Name: `defi-backend`
   - Region: `us-central1-a`
   - Machine: `e2-medium`
   - OS: Ubuntu 22.04 LTS
   - Disk: 30GB
   - Firewall: ✅ HTTP, ✅ HTTPS
5. Create firewall rule:
   - Name: `allow-backend-8000`
   - Port: 8000
   - Source: 0.0.0.0/0
6. **SAVE your External IP!** (e.g., `34.123.45.67`)

### 2.2: Run Automated Setup (40 min)

**Click "SSH" button in GCP console**, then run:

```bash
# Download and run setup script
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/backend/deploy/gcp_tinyllama_setup.sh
chmod +x gcp_tinyllama_setup.sh
./gcp_tinyllama_setup.sh
```

**When prompted:**
- Enter your GitHub repo URL
- Wait 30-40 minutes for completion

### 2.3: Initialize Vector Store (10 min)

```bash
# Still in SSH terminal
curl -X POST http://localhost:8000/api/v1/llm/initialize

# Wait 5-10 minutes for completion
```

### 2.4: Test Backend (5 min)

```bash
# Test health
curl http://localhost:8000/api/v1/health

# Test LLM
curl http://localhost:8000/api/v1/llm/health

# Test query
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What protocols are monitored?"}'
```

✅ **If all tests pass, backend is ready!**

---

## 🎯 Step 3: Deploy Frontend (30 min)

### 3.1: Update Frontend Config (5 min)

**On your local machine:**

```bash
cd frontend

# Create .env.production file
# Add this line (replace with YOUR External IP):
echo "VITE_API_BASE_URL=http://34.123.45.67:8000" > .env.production

# Commit and push
git add .
git commit -m "Add production config and AI assistant"
git push origin main
```

### 3.2: Deploy to Vercel (15 min)

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "Add New Project"
4. Import your repository
5. Configure:
   - Framework: **Vite**
   - Root: **frontend**
   - Build: `npm run build`
   - Output: **dist**
6. Add environment variable:
   - Key: `VITE_API_BASE_URL`
   - Value: `http://YOUR_GCP_IP:8000`
7. Click **"Deploy"**
8. Wait 2-3 minutes
9. **Save your Vercel URL!**

### 3.3: Enable CORS (10 min)

**SSH back into GCP:**

```bash
gcloud compute ssh defi-backend --zone=us-central1-a

cd ~/defi-project/backend
nano app/main.py
```

**Find CORS section and change to:**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Save (Ctrl+X, Y, Enter) and restart:**

```bash
sudo systemctl restart defi-backend
```

---

## 🎯 Step 4: Test Everything (10 min)

### 4.1: Open Your Dashboard

Open your Vercel URL in browser: `https://your-project.vercel.app`

### 4.2: Check All Tabs

- [ ] 🔥 Risk Heatmap - Shows protocols
- [ ] 📊 7-Day Analysis - Shows charts
- [ ] 💼 Portfolio - Works
- [ ] 🤖 AI Assistant - **NEW!** Shows "ONLINE"

### 4.3: Test AI Assistant

1. Click "🤖 AI Assistant" tab
2. Type: "What are the high-risk protocols?"
3. Click Send
4. **You should get a response!** 🎉

---

## ✅ Success! You're Live!

**Your URLs:**
- Dashboard: `https://your-project.vercel.app`
- API: `http://YOUR_GCP_IP:8000`
- API Docs: `http://YOUR_GCP_IP:8000/docs`

**Try asking your AI:**
- "Show me Aave's risk score"
- "Which protocols have the highest TVL?"
- "What factors contribute to protocol risk?"

---

## 💰 Monthly Cost

**$0/month** for 12 months (uses your $300 GCP credit!)

- GCP e2-medium: ~$24/month
- Vercel: $0/month (free forever)
- **Total: Covered by your free credit**

---

## 📚 Full Documentation

If you need more details:
- **Complete guide**: `COMPLETE_DEPLOYMENT_GUIDE.md`
- **Checklist**: `LLM_SETUP_CHECKLIST.md`
- **Backend details**: `GCP_TINYLLAMA_SETUP.md`
- **Frontend details**: `FRONTEND_DEPLOYMENT.md`

---

## 🆘 Quick Troubleshooting

**Dashboard shows no data?**
- Check CORS is enabled (Step 3.3)
- Check API URL in Vercel environment variables

**AI Assistant shows OFFLINE?**
```bash
curl http://YOUR_GCP_IP:8000/api/v1/llm/health
```

**Backend not responding?**
```bash
sudo systemctl status defi-backend
sudo journalctl -u defi-backend -f
```

---

## 🎯 Ready?

**Start with Step 1 above!**

Each step has detailed instructions in `COMPLETE_DEPLOYMENT_GUIDE.md` if needed.

**Let me know when you complete each step or if you hit any issues!** 🚀

