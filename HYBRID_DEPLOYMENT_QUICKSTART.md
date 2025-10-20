# 🚀 Hybrid Deployment Quick Start

## What is Hybrid Deployment?

**Backend on GCP Free Tier** ($0) + **Ollama Locally** ($0) = **$0/month Total** 🎉

```
Your Machine (Ollama) ←→ GCP Free Tier (Backend) ←→ Users
```

---

## ⚡ Quick Setup (30 Minutes)

### Part 1: Local Machine (5 min)

```bash
# 1. Install Ollama
curl https://ollama.ai/install.sh | sh  # Linux/macOS
# OR: winget install Ollama.Ollama       # Windows

# 2. Pull models
ollama pull mistral
ollama pull nomic-embed-text

# 3. Choose connection method and run setup
cd backend/deploy
chmod +x local_ollama_setup.sh
./local_ollama_setup.sh
```

**You'll get a URL like:**
- Tailscale: `http://100.x.x.x:11434`
- ngrok: `https://abc123.ngrok.io`
- Direct: `http://YOUR_IP:11434`

**Save this URL!** You'll need it for GCP setup.

---

### Part 2: GCP Setup (15 min)

#### A. Create VM Instance

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Compute Engine → VM Instances → Create
3. Settings:
   - Name: `defi-backend`
   - Region: `us-central1` (free tier)
   - Machine: `e2-micro`
   - Boot disk: Ubuntu 22.04 LTS, 30GB
   - ✅ Allow HTTP/HTTPS traffic
4. Create

#### B. Configure Firewall

```bash
# Allow backend port
gcloud compute firewall-rules create allow-backend \
  --allow=tcp:8000 \
  --source-ranges=0.0.0.0/0
```

#### C. SSH and Run Setup

```bash
# SSH into instance
gcloud compute ssh defi-backend --zone=us-central1-a

# Download and run setup script
curl -O https://raw.githubusercontent.com/YOUR_REPO/main/backend/deploy/gcp_setup.sh
chmod +x gcp_setup.sh
./gcp_setup.sh
```

**When prompted:**
- Enter your GitHub repo URL
- Enter the Ollama URL from Part 1

---

### Part 3: Test (5 min)

```bash
# Get your GCP IP
gcloud compute instances list

# Test from your local machine
export GCP_IP=YOUR_GCP_IP

# 1. Test backend
curl http://$GCP_IP:8000/api/v1/health

# 2. Test LLM
curl http://$GCP_IP:8000/api/v1/llm/health

# 3. Initialize vector store
curl -X POST http://$GCP_IP:8000/api/v1/llm/initialize

# 4. Test query
curl -X POST http://$GCP_IP:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What protocols are monitored?"}'
```

---

## ✅ Success Checklist

- [ ] Local Ollama running and accessible
- [ ] GCP VM created (e2-micro)
- [ ] Backend service running on GCP
- [ ] Health checks pass
- [ ] Vector store initialized
- [ ] LLM queries work

---

## 📊 What You Get

| Component | Location | Cost |
|-----------|----------|------|
| **Ollama + Mistral** | Your machine | $0 |
| **FastAPI Backend** | GCP e2-micro | $0 (free tier) |
| **PostgreSQL** | GCP VM | $0 (included) |
| **Vector Store** | GCP VM | $0 (included) |
| **Storage (30GB)** | GCP | $0 (free tier) |
| **Network (1GB/mo)** | GCP | $0 (free tier) |
| **TOTAL** | | **$0/month** ✅ |

---

## 🔧 Connection Options

### Option 1: Tailscale (Recommended)
**Pros:** Secure, static IP, free  
**Setup:** 5 minutes  
**Best for:** Production use

### Option 2: ngrok
**Pros:** Easy, works anywhere  
**Cons:** URL changes on restart (free tier)  
**Setup:** 2 minutes  
**Best for:** Testing

### Option 3: Direct IP
**Pros:** No third-party  
**Cons:** Requires port forwarding  
**Setup:** 10 minutes  
**Best for:** Advanced users with static IP

---

## 📚 Full Documentation

- **Complete Guide**: `markdowns/HYBRID_DEPLOYMENT_GCP.md`
- **Troubleshooting**: See full guide
- **Security**: See full guide
- **Monitoring**: See full guide

---

## 🆘 Common Issues

### "Backend can't connect to Ollama"

1. **Check local Ollama:**
   ```bash
   curl http://localhost:11434
   ```

2. **Check tunnel (if using Tailscale/ngrok):**
   ```bash
   # Tailscale
   tailscale status
   
   # ngrok
   curl http://localhost:4040/api/tunnels
   ```

3. **Test from GCP:**
   ```bash
   # SSH into GCP
   curl $OLLAMA_BASE_URL  # Use URL from .env
   ```

### "Vector store initialization fails"

```bash
# SSH into GCP
cd ~/defi-risk-assessment/backend
source venv/bin/activate
curl -X POST http://localhost:8000/api/v1/llm/initialize
```

### "Slow responses"

- Use Tailscale instead of ngrok (faster)
- Reduce `RAG_TOP_K=3` in `.env`
- Mistral is already fast - good choice!

---

## 🎯 Next Steps

1. **Deploy Frontend**
   - Vercel (free)
   - Netlify (free)
   - GitHub Pages (free)

2. **Add Custom Domain**
   - Freenom (free)
   - Cloudflare DNS (free)

3. **Enable HTTPS**
   - Let's Encrypt (free)
   - Cloudflare (free)

4. **Set Up Monitoring**
   - GCP Cloud Monitoring (free tier)
   - Uptime checks (free)

---

## 💡 Pro Tips

1. **Keep ngrok running 24/7** (or use Tailscale)
2. **Set up systemd** for auto-restart (done by script)
3. **Monitor logs**: `sudo journalctl -u defi-backend -f`
4. **Backup database** weekly
5. **Update code**: `git pull && sudo systemctl restart defi-backend`

---

## 🎉 You Did It!

You now have a **production-ready hybrid deployment** running for **$0/month**!

**Your Setup:**
- ✅ Fast local LLM (Mistral)
- ✅ Scalable backend (GCP)
- ✅ Secure connection (Tailscale/ngrok)
- ✅ Complete privacy (LLM data stays local)
- ✅ Zero monthly costs

Start using your API:
```bash
curl -X POST http://YOUR_GCP_IP:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me high-risk protocols"}'
```

🚀 Happy deploying!


