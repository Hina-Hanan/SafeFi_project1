# 🌐 Hybrid Deployment: GCP Backend + Local Ollama

## 🎯 Architecture Overview

This guide shows how to deploy your DeFi Risk Assessment platform using a **hybrid architecture** that stays **100% free**:

```
┌─────────────────────────────┐
│   Your Local Machine        │
│  ┌────────────────────┐     │
│  │  Ollama + Mistral  │     │  ← FREE: Run on your hardware
│  │  (localhost:11434) │     │     No RAM/CPU limits
│  └─────────┬──────────┘     │     Complete privacy
└────────────┼─────────────────┘
             │
             │ Secure Tunnel (VPN/SSH/ngrok)
             │
             ↓
┌─────────────────────────────┐
│   Google Cloud Platform     │
│      (Free Tier)            │
│  ┌────────────────────┐     │
│  │   FastAPI Backend  │     │  ← FREE: e1-micro instance
│  │   PostgreSQL DB    │     │     0.6GB RAM, 30GB storage
│  │   Vector Store     │     │     Database, API, vector search
│  └────────────────────┘     │
└─────────────────────────────┘
             ↕
         Internet
             ↕
┌─────────────────────────────┐
│   Frontend (Anywhere)       │
│  - Vercel (free)            │  ← FREE: Static hosting
│  - Netlify (free)           │     React app
│  - GitHub Pages (free)      │     User interface
└─────────────────────────────┘
```

### Benefits

✅ **$0/month** - Everything runs on free tiers  
✅ **Fast LLM** - Mistral runs on your powerful local hardware  
✅ **Scalable Backend** - GCP handles HTTP/DB traffic  
✅ **Private Data** - LLM processing stays local  
✅ **Low Latency** - Backend responds quickly from cloud  

---

## 📋 Prerequisites

### Local Machine
- 8GB+ RAM
- Windows/macOS/Linux
- Internet connection with static IP (or dynamic DNS)

### GCP Account
- Free tier account (new users get $300 credit + always free)
- Credit card for verification (won't be charged)

### Domain (Optional)
- Free domain from Freenom or use GCP IP
- Or use ngrok/Tailscale for easy setup

---

## 🚀 Part 1: Setup Local Ollama for Remote Access

### Step 1.1: Install Ollama

```bash
# Windows
winget install Ollama.Ollama

# macOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh
```

### Step 1.2: Pull Mistral Model

```bash
ollama pull mistral
```

### Step 1.3: Configure for Remote Access

**Option A: Using ngrok (Easiest)**

```bash
# Install ngrok
# Windows: winget install ngrok
# macOS: brew install ngrok
# Linux: snap install ngrok

# Sign up at ngrok.com for free account
ngrok authtoken YOUR_TOKEN

# Expose Ollama (keep this running)
ngrok http 11434
```

You'll get a URL like: `https://abc123.ngrok.io`

**Option B: Using Tailscale VPN (Most Secure)**

```bash
# Install Tailscale
# Windows: winget install tailscale
# macOS: brew install tailscale
# Linux: curl -fsSL https://tailscale.com/install.sh | sh

# Start Tailscale
tailscale up

# Get your Tailscale IP
tailscale ip -4
```

You'll get an IP like: `100.x.x.x`

**Option C: Direct Expose (If You Have Static IP)**

```bash
# Configure Ollama to listen on all interfaces
# Windows: Set environment variable
setx OLLAMA_HOST "0.0.0.0"

# macOS/Linux: Add to ~/.bashrc or ~/.zshrc
export OLLAMA_HOST=0.0.0.0

# Start Ollama
ollama serve
```

Forward port 11434 on your router.

### Step 1.4: Test Local Ollama

```bash
# Test locally first
curl http://localhost:11434

# Test from external (replace with your method)
# ngrok: curl https://abc123.ngrok.io
# Tailscale: curl http://100.x.x.x:11434
# Direct: curl http://YOUR_PUBLIC_IP:11434
```

---

## ☁️ Part 2: Deploy Backend to GCP Free Tier

### Step 2.1: Create GCP Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create new project: "defi-risk-assessment"
3. Enable billing (stays in free tier)

### Step 2.2: Create VM Instance

```bash
# Via gcloud CLI (or use web console)
gcloud compute instances create defi-backend \
  --zone=us-central1-a \
  --machine-type=e2-micro \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=30GB \
  --tags=http-server,https-server
```

**Or via Console:**
1. Compute Engine → VM Instances → Create
2. Name: `defi-backend`
3. Region: `us-central1` (free tier eligible)
4. Machine type: `e2-micro` (0.25-2 vCPUs, 1GB RAM)
5. Boot disk: Ubuntu 22.04 LTS, 30GB
6. Allow HTTP/HTTPS traffic
7. Create

### Step 2.3: Configure Firewall

```bash
# Allow backend port (8000)
gcloud compute firewall-rules create allow-backend \
  --allow=tcp:8000 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=http-server
```

### Step 2.4: SSH into Instance

```bash
gcloud compute ssh defi-backend --zone=us-central1-a
```

### Step 2.5: Install Dependencies on GCP

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip git

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Configure PostgreSQL
sudo -u postgres psql -c "CREATE USER defi_user WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "CREATE DATABASE defi_risk_assessment OWNER defi_user;"
```

### Step 2.6: Clone and Setup Backend

```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/your-repo.git
cd your-repo/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2.7: Configure Environment Variables

```bash
# Create .env file
cat > .env << EOF
# Database
DATABASE_URL=postgresql+psycopg2://defi_user:your_secure_password@localhost:5432/defi_risk_assessment

# Ollama Configuration (IMPORTANT: Point to your local Ollama)
OLLAMA_BASE_URL=https://abc123.ngrok.io  # Or your Tailscale IP: http://100.x.x.x:11434
OLLAMA_MODEL=mistral
OLLAMA_TEMPERATURE=0.7

# RAG Configuration
RAG_TOP_K=5
VECTOR_STORE_PATH=/home/YOUR_USERNAME/vectorstore

# Environment
ENVIRONMENT=production
EOF
```

**Important:** Replace `OLLAMA_BASE_URL` with:
- **ngrok**: `https://abc123.ngrok.io`
- **Tailscale**: `http://100.x.x.x:11434`
- **Direct**: `http://YOUR_PUBLIC_IP:11434`

### Step 2.8: Initialize Database

```bash
# Run database migrations
python -m alembic upgrade head

# Seed data (optional)
python scripts/seed_real_protocols.py
```

### Step 2.9: Initialize Vector Store

```bash
# Start backend temporarily
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Initialize vector store
curl -X POST http://localhost:8000/api/v1/llm/initialize

# Stop background process
pkill -f uvicorn
```

### Step 2.10: Setup Systemd Service

```bash
# Create systemd service
sudo tee /etc/systemd/system/defi-backend.service > /dev/null << EOF
[Unit]
Description=DeFi Risk Assessment Backend
After=network.target postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/your-repo/backend
Environment="PATH=/home/$USER/your-repo/backend/venv/bin"
ExecStart=/home/$USER/your-repo/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable defi-backend
sudo systemctl start defi-backend

# Check status
sudo systemctl status defi-backend
```

---

## 🔐 Part 3: Secure Connection Setup

### Option A: ngrok (Easiest)

**Advantages:**
- ✅ No firewall configuration
- ✅ HTTPS automatic
- ✅ Works from anywhere
- ✅ Free tier available

**Setup:**

1. Keep ngrok running on local machine:
```bash
ngrok http 11434
```

2. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

3. Update GCP backend `.env`:
```bash
OLLAMA_BASE_URL=https://abc123.ngrok.io
```

4. Restart backend:
```bash
sudo systemctl restart defi-backend
```

**Note:** Free ngrok URLs change on restart. Consider paid plan ($8/month) for static URLs, or use Tailscale.

---

### Option B: Tailscale VPN (Most Secure)

**Advantages:**
- ✅ Encrypted VPN tunnel
- ✅ Static IPs
- ✅ Completely free
- ✅ No port forwarding needed

**Setup:**

1. **Install Tailscale on local machine:**
```bash
# Already done in Step 1.3
tailscale up
```

2. **Install Tailscale on GCP instance:**
```bash
# SSH into GCP instance
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

3. **Authorize both devices** in Tailscale admin panel

4. **Get local machine's Tailscale IP:**
```bash
# On local machine
tailscale ip -4
# Example output: 100.64.1.2
```

5. **Update GCP backend `.env`:**
```bash
OLLAMA_BASE_URL=http://100.64.1.2:11434
```

6. **Start Ollama on all interfaces:**
```bash
# On local machine
OLLAMA_HOST=0.0.0.0 ollama serve
```

7. **Test from GCP:**
```bash
# On GCP instance
curl http://100.64.1.2:11434
```

8. **Restart backend:**
```bash
sudo systemctl restart defi-backend
```

---

### Option C: SSH Tunnel

**Advantages:**
- ✅ No additional software
- ✅ Encrypted
- ✅ Free

**Setup:**

1. **Enable SSH access to your local machine**

2. **On GCP, create reverse SSH tunnel:**
```bash
# Create persistent tunnel
ssh -N -L 11434:localhost:11434 user@YOUR_HOME_IP

# Or use autossh for automatic reconnection
sudo apt install autossh
autossh -M 0 -N -L 11434:localhost:11434 user@YOUR_HOME_IP
```

3. **Backend uses localhost:**
```bash
OLLAMA_BASE_URL=http://localhost:11434
```

---

## 🧪 Part 4: Testing the Hybrid Setup

### Test 1: Ollama Connectivity

```bash
# From GCP instance
curl $OLLAMA_BASE_URL

# Expected: "Ollama is running"
```

### Test 2: Backend Health

```bash
# From anywhere
curl http://YOUR_GCP_IP:8000/api/v1/health

# Expected: {"status": "ok", "database_connected": true}
```

### Test 3: LLM Health

```bash
curl http://YOUR_GCP_IP:8000/api/v1/llm/health

# Expected: {"ollama_available": true, "vector_store_initialized": true}
```

### Test 4: LLM Query

```bash
curl -X POST http://YOUR_GCP_IP:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What protocols are monitored?"}'

# Expected: {"answer": "We are currently monitoring...", "context_used": 5}
```

---

## 📊 Monitoring & Maintenance

### Monitor Backend Logs

```bash
# On GCP instance
sudo journalctl -u defi-backend -f
```

### Monitor Ollama on Local Machine

```bash
# Check if Ollama is running
curl http://localhost:11434

# Check ngrok status (if using)
curl http://127.0.0.1:4040/api/tunnels
```

### Refresh Vector Store

```bash
# Monthly or after major data updates
curl -X POST http://YOUR_GCP_IP:8000/api/v1/llm/refresh
```

### Update Backend Code

```bash
# SSH into GCP
cd ~/your-repo
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart defi-backend
```

---

## 💰 Cost Breakdown

### Monthly Costs

| Service | Tier | Cost |
|---------|------|------|
| **Local Ollama** | Hardware | $0 |
| **GCP e2-micro** | Free tier | $0 |
| **GCP Storage (30GB)** | Free tier | $0 |
| **GCP Network (1GB/month)** | Free tier | $0 |
| **Tailscale VPN** | Free | $0 |
| **OR ngrok Free** | Free | $0 |
| **Total** | | **$0/month** ✅ |

### Optional Paid Upgrades

| Service | Cost | Why? |
|---------|------|------|
| ngrok Pro | $8/month | Static URLs |
| GCP e2-small | $13/month | More RAM for faster API |
| Custom domain | $12/year | Professional URL |

---

## 🔧 Troubleshooting

### Issue: Backend can't connect to Ollama

**Check:**
1. Is Ollama running locally?
   ```bash
   curl http://localhost:11434
   ```

2. Is tunnel active?
   ```bash
   # ngrok
   curl http://127.0.0.1:4040/api/tunnels
   
   # Tailscale
   tailscale status
   ```

3. Is `OLLAMA_BASE_URL` correct in GCP `.env`?

4. Test from GCP:
   ```bash
   curl $OLLAMA_BASE_URL
   ```

---

### Issue: Vector store initialization fails

**Solution:**
```bash
# SSH into GCP
cd ~/your-repo/backend
source venv/bin/activate
python -c "from app.services.rag.vector_store import initialize_vector_store; from app.database.connection import get_db; initialize_vector_store(next(get_db()))"
```

---

### Issue: Slow LLM responses

**Causes:**
- Network latency between GCP and local machine
- Ollama overloaded

**Solutions:**
1. Use Tailscale VPN (faster than ngrok)
2. Increase Ollama timeout in `.env`:
   ```bash
   OLLAMA_TIMEOUT=300
   ```
3. Use smaller model (already using Mistral - good choice!)

---

### Issue: ngrok URL changes on restart

**Solutions:**
1. Keep ngrok running 24/7
2. Use ngrok paid plan for static URLs ($8/month)
3. **Better:** Switch to Tailscale (free, static IPs)
4. Create a script to auto-update GCP `.env` when ngrok restarts

---

## 🚀 Performance Optimization

### 1. Enable Caching

```python
# Add to backend/app/api/v1/llm_assistant.py
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(query: str) -> str:
    # Cache common queries
    pass
```

### 2. Use Connection Pooling

Already configured in SQLAlchemy.

### 3. Optimize Vector Search

```bash
# In .env, reduce search results if slow
RAG_TOP_K=3  # Instead of 5
```

### 4. Use FAISS Instead of ChromaDB

Already configured by default (faster in-memory search).

---

## 📈 Scaling Beyond Free Tier

If you outgrow the free tier:

### Option 1: Upgrade GCP Instance

```bash
# Upgrade to e2-small (2GB RAM)
gcloud compute instances set-machine-type defi-backend \
  --machine-type=e2-small \
  --zone=us-central1-a
```

**Cost:** ~$13/month

### Option 2: Move Ollama to GCP

Only if you need:
- 24/7 availability without local machine
- Lower latency
- Professional setup

**Requirements:**
- e2-standard-2 instance (8GB RAM) - ~$50/month
- Or use cloud LLM APIs (OpenAI) - ~$100-500/month

---

## ✅ Summary

You now have a **complete hybrid deployment**:

✅ **Backend on GCP** - Free tier, handles HTTP/DB/vector search  
✅ **Ollama locally** - Free, runs on your hardware  
✅ **Secure tunnel** - Tailscale/ngrok/SSH  
✅ **$0/month cost** - Everything on free tiers  
✅ **Production-ready** - Systemd service, monitoring, logs  

### Next Steps

1. Deploy frontend to Vercel/Netlify (free)
2. Set up custom domain (optional)
3. Configure SSL/HTTPS
4. Set up monitoring (GCP Cloud Monitoring - free)
5. Create backup strategy

---

**Congratulations! You have a production hybrid deployment running for free!** 🎉

