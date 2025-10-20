# ⚡ GCP + TinyLlama Quickstart (2 Hours)

## 🎯 What You're Building

**Complete LLM system on GCP Free Tier:**
- Backend + Database + TinyLlama on single GCP instance
- No local machine needed
- $0/month (uses your $300 credit)
- Accessible from anywhere

---

## 📋 Prerequisites

- ✅ Google Cloud account with $300 free credit
- ✅ GitHub repository with your code
- ✅ 2 hours of time

---

## 🚀 Step-by-Step Guide

### Step 1: Clean Up Local Machine (5 min)

**Remove Mistral to free up space:**

```bash
# Stop Ollama if running
# Windows: taskkill /F /IM ollama.exe
# Mac/Linux: pkill ollama

# Remove models
ollama rm mistral
ollama rm nomic-embed-text

# (Optional) Uninstall Ollama completely
# Windows: winget uninstall Ollama.Ollama
# Mac: brew uninstall ollama
```

**✅ Done!** You've freed ~5GB space.

---

### Step 2: Create GCP Instance (10 min)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create project: `defi-risk-assessment`
3. Enable Compute Engine API
4. Create VM Instance:
   - Name: `defi-backend`
   - Region: `us-central1` (free tier)
   - Machine: `e2-medium` (2 vCPU, 4GB RAM)
   - OS: Ubuntu 22.04 LTS
   - Disk: 30GB
   - Firewall: ✅ HTTP, ✅ HTTPS
5. Create firewall rule for port 8000:
   - Name: `allow-backend-8000`
   - Target: All instances
   - Source: 0.0.0.0/0
   - Protocol: TCP, Port: 8000

**✅ Note your External IP!**

---

### Step 3: Run Automated Setup (40 min)

**SSH into instance:**
```bash
# Via browser: Click "SSH" button in console
# Or via CLI:
gcloud compute ssh defi-backend --zone=us-central1-a
```

**Run setup script:**
```bash
# Download setup script
curl -O https://raw.githubusercontent.com/YOUR_REPO/main/backend/deploy/gcp_tinyllama_setup.sh

# Make executable
chmod +x gcp_tinyllama_setup.sh

# Run it
./gcp_tinyllama_setup.sh

# Enter your GitHub repo URL when prompted
# Wait 30-40 minutes for completion...
```

**The script will:**
- ✅ Install Python, PostgreSQL, Ollama
- ✅ Pull TinyLlama model
- ✅ Setup database
- ✅ Install backend dependencies
- ✅ Configure systemd services
- ✅ Start everything automatically

---

### Step 4: Initialize Vector Store (10 min)

**Still in SSH terminal:**
```bash
# Initialize RAG vector store
curl -X POST http://localhost:8000/api/v1/llm/initialize

# This takes 5-10 minutes
# Wait for: {"initialized":true,"document_count":XX}
```

---

### Step 5: Test Everything (10 min)

**From your local machine:**
```bash
# Replace with your GCP External IP
export GCP_IP=YOUR_IP_HERE

# Test health
curl http://$GCP_IP:8000/api/v1/health

# Test LLM
curl http://$GCP_IP:8000/api/v1/llm/health

# Test query
curl -X POST http://$GCP_IP:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What protocols are monitored?"}'

# Or download test script
curl -O https://raw.githubusercontent.com/YOUR_REPO/main/backend/deploy/test_gcp_deployment.sh
chmod +x test_gcp_deployment.sh
./test_gcp_deployment.sh
# Enter your GCP IP when prompted
```

---

## ✅ Success Checklist

- [ ] GCP instance created (e2-medium)
- [ ] Setup script completed successfully
- [ ] Backend service running
- [ ] Ollama service running
- [ ] Vector store initialized
- [ ] Health checks pass
- [ ] LLM queries work from local machine

---

## 🎉 You're Done!

**Your live URLs:**
- API: `http://YOUR_GCP_IP:8000`
- Docs: `http://YOUR_GCP_IP:8000/docs`
- Health: `http://YOUR_GCP_IP:8000/api/v1/health`

**Try it:**
```bash
curl -X POST http://YOUR_GCP_IP:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Show me high-risk DeFi protocols"}'
```

---

## 📊 What You Have

| Component | Location | Status |
|-----------|----------|--------|
| Backend | GCP e2-medium | ✅ Running |
| Database | Same GCP | ✅ Running |
| TinyLlama | Same GCP | ✅ Running |
| Vector Store | Same GCP | ✅ Initialized |
| Auto-restart | systemd | ✅ Configured |

**Monthly Cost:** ~$24/month (uses your $300 credit = 12 months free!)

---

## 🔧 Management Commands

**SSH into GCP:**
```bash
gcloud compute ssh defi-backend --zone=us-central1-a
```

**View logs:**
```bash
# Backend logs
sudo journalctl -u defi-backend -f

# Ollama logs
sudo journalctl -u ollama -f
```

**Restart services:**
```bash
sudo systemctl restart defi-backend
sudo systemctl restart ollama
```

**Update code:**
```bash
cd ~/defi-project
git pull
sudo systemctl restart defi-backend
```

**Refresh vector store:**
```bash
curl -X POST http://localhost:8000/api/v1/llm/refresh
```

---

## 🎯 Next Steps

1. **Deploy Frontend:**
   - Vercel (free): https://vercel.com
   - Update API URL to: `http://YOUR_GCP_IP:8000`

2. **Enable HTTPS:**
   - Use Cloudflare (free)
   - Or Let's Encrypt

3. **Add Monitoring:**
   - GCP Cloud Monitoring (free tier)

4. **Upgrade Model (Optional):**
   - If TinyLlama isn't powerful enough
   - Upgrade to e2-standard-2 (8GB RAM)
   - Install Mistral or Llama3

---

## 💡 TinyLlama vs Others

| Model | RAM | Speed | Quality | Use |
|-------|-----|-------|---------|-----|
| **TinyLlama** | 1GB | ⚡⚡⚡ | ⭐⭐⭐ | ✅ Current |
| Mistral | 8GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Upgrade |
| Llama3 | 8GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Upgrade |

TinyLlama is **3x faster** than Mistral but with **70% quality**.

**Good enough for:**
- ✅ Basic Q&A
- ✅ Information retrieval
- ✅ Simple analysis

**Not good for:**
- ❌ Complex reasoning
- ❌ Code generation
- ❌ Long documents

---

## 🆘 Troubleshooting

### Backend not starting?
```bash
# Check logs
sudo journalctl -u defi-backend -n 50

# Test manually
cd ~/defi-project/backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Ollama not working?
```bash
# Check status
sudo systemctl status ollama

# Test
curl http://localhost:11434

# Restart
sudo systemctl restart ollama
```

### Vector store initialization fails?
```bash
# Check database connection
psql -U defi_user -d defi_risk_assessment -h localhost

# Check if models are installed
ollama list

# Try again
curl -X POST http://localhost:8000/api/v1/llm/initialize
```

---

## 📚 Full Documentation

- **Complete Guide**: `GCP_TINYLLAMA_SETUP.md`
- **Cleanup Guide**: `CLEANUP_LOCAL.md`
- **Test Script**: `backend/deploy/test_gcp_deployment.sh`

---

**Ready? Start with Step 1!** 🚀

Total time: ~2 hours from start to finish.

