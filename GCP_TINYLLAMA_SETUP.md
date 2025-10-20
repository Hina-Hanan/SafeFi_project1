# 🚀 GCP + TinyLlama Setup Guide (Complete in 2 Hours)

## Overview

**What we're building:**
- ✅ Backend on GCP e2-micro (free tier)
- ✅ TinyLlama running on same GCP instance
- ✅ All RAG features working
- ✅ **Total cost: $0/month**

**No local machine needed!** Everything runs in the cloud.

---

## Timeline

- **0:00-0:30** - GCP Setup & Instance Creation
- **0:30-1:00** - Install Dependencies & Backend
- **1:00-1:30** - Install TinyLlama & Initialize RAG
- **1:30-2:00** - Testing & Verification

---

## PART 1: GCP SETUP (30 minutes)

### Step 1.1: Create GCP Project (5 min)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Name: `defi-risk-assessment`
4. Click "Create"
5. Wait for project creation (1-2 minutes)

### Step 1.2: Enable Compute Engine (2 min)

1. In the search bar, type "Compute Engine"
2. Click "Compute Engine API"
3. Click "Enable"
4. Wait for API to enable

### Step 1.3: Create VM Instance (10 min)

**Via Console (Easier):**

1. Go to **Compute Engine** → **VM Instances**
2. Click **"Create Instance"**
3. Configure:

```
Name: defi-backend
Region: us-central1 (Iowa) ← Free tier eligible!
Zone: us-central1-a

Machine Configuration:
- Series: E2
- Machine type: e2-medium (2 vCPUs, 4GB RAM)
  ⚠️ NOTE: Use e2-medium not e2-micro for TinyLlama
  Cost: ~$24/month, but use your $300 free credit

Boot disk:
- Click "Change"
- Operating system: Ubuntu
- Version: Ubuntu 22.04 LTS
- Boot disk type: Standard persistent disk
- Size: 30 GB
- Click "Select"

Firewall:
- ✅ Allow HTTP traffic
- ✅ Allow HTTPS traffic

Click "Create"
```

**Wait 1-2 minutes** for instance to start.

### Step 1.4: Configure Firewall (3 min)

1. Go to **VPC Network** → **Firewall**
2. Click **"Create Firewall Rule"**
3. Configure:

```
Name: allow-backend-8000
Network: default
Priority: 1000
Direction: Ingress
Action: Allow
Targets: All instances in the network
Source IP ranges: 0.0.0.0/0
Protocols and ports:
  ✅ TCP: 8000

Click "Create"
```

### Step 1.5: Note Your External IP (1 min)

1. Go back to **VM Instances**
2. Find your `defi-backend` instance
3. **Copy the External IP** (e.g., `34.123.45.67`)
4. **Save it** - you'll need it!

---

## PART 2: BACKEND INSTALLATION (30 minutes)

### Step 2.1: SSH into Instance (2 min)

**Via Browser (Easiest):**
1. Go to **VM Instances**
2. Click **"SSH"** button next to your instance
3. Browser SSH window opens

**Or via gcloud CLI:**
```bash
gcloud compute ssh defi-backend --zone=us-central1-a
```

### Step 2.2: Install System Dependencies (10 min)

**Run these commands in the SSH terminal:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install other dependencies
sudo apt install -y git curl build-essential

# Verify installations
python3.11 --version
psql --version
```

### Step 2.3: Setup PostgreSQL (5 min)

```bash
# Generate secure password
DB_PASSWORD=$(openssl rand -base64 20)
echo "Database Password: $DB_PASSWORD"
echo $DB_PASSWORD > ~/db_password.txt
echo "⚠️ SAVE THIS PASSWORD!"

# Create database user and database
sudo -u postgres psql << EOF
CREATE USER defi_user WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE defi_risk_assessment OWNER defi_user;
GRANT ALL PRIVILEGES ON DATABASE defi_risk_assessment TO defi_user;
\q
EOF

echo "✅ PostgreSQL setup complete"
```

### Step 2.4: Clone Repository (5 min)

```bash
# Clone your repository
cd ~
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git defi-project

# If private repo, you'll need to authenticate
# Use Personal Access Token for authentication

cd defi-project/backend
```

### Step 2.5: Setup Python Environment (8 min)

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# This takes 5-8 minutes
# Wait for it to complete...
```

---

## PART 3: INSTALL TINYLLAMA (30 minutes)

### Step 3.1: Install Ollama (5 min)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
ollama --version
```

### Step 3.2: Pull TinyLlama (10 min)

```bash
# Pull TinyLlama (1.1GB - small and fast!)
ollama pull tinyllama

# This takes about 5-10 minutes depending on connection
# Wait for download to complete...

# Verify model is installed
ollama list
# Should show: tinyllama

# Pull embedding model (smaller one)
ollama pull all-minilm

# Verify both models
ollama list
```

### Step 3.3: Start Ollama as Service (5 min)

```bash
# Create systemd service for Ollama
sudo tee /etc/systemd/system/ollama.service > /dev/null << 'EOF'
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
ExecStart=/usr/local/bin/ollama serve
Environment="OLLAMA_HOST=127.0.0.1:11434"
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Replace YOUR_USERNAME with your actual username
sudo sed -i "s/YOUR_USERNAME/$USER/g" /etc/systemd/system/ollama.service

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama

# Check status
sudo systemctl status ollama

# Test Ollama
sleep 3
curl http://localhost:11434
# Should return: "Ollama is running"
```

### Step 3.4: Configure Backend Environment (5 min)

```bash
# Go to backend directory
cd ~/defi-project/backend

# Read the database password
DB_PASSWORD=$(cat ~/db_password.txt)

# Create .env file
cat > .env << EOF
# Database
DATABASE_URL=postgresql+psycopg2://defi_user:${DB_PASSWORD}@localhost:5432/defi_risk_assessment

# Ollama (Local on same machine)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
OLLAMA_TEMPERATURE=0.7
OLLAMA_TIMEOUT=120
OLLAMA_EMBEDDING_MODEL=all-minilm

# RAG Configuration
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_TOP_K=5
VECTOR_STORE_PATH=/home/$USER/vectorstore

# MLflow
MLFLOW_TRACKING_URI=file:///home/$USER/mlruns

# Environment
ENVIRONMENT=production
EOF

echo "✅ Environment configured"
cat .env
```

### Step 3.5: Initialize Database (5 min)

```bash
# Make sure venv is activated
source venv/bin/activate

# Run database migrations (if you have them)
if [ -f alembic.ini ]; then
    python -m alembic upgrade head
fi

# Seed initial data (if you have seed script)
if [ -f scripts/seed_real_protocols.py ]; then
    python scripts/seed_real_protocols.py
fi

echo "✅ Database initialized"
```

---

## PART 4: START & TEST (30 minutes)

### Step 4.1: Create Backend Service (5 min)

```bash
# Create systemd service for backend
sudo tee /etc/systemd/system/defi-backend.service > /dev/null << EOF
[Unit]
Description=DeFi Risk Assessment Backend
After=network.target postgresql.service ollama.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/defi-project/backend
Environment="PATH=/home/$USER/defi-project/backend/venv/bin"
ExecStart=/home/$USER/defi-project/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
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

### Step 4.2: Test Backend (5 min)

```bash
# Test locally on server
curl http://localhost:8000/api/v1/health

# Should return:
# {"status":"ok","database_connected":true,...}
```

### Step 4.3: Initialize Vector Store (10 min)

```bash
# This creates embeddings from your database
# Takes 5-10 minutes depending on data size
curl -X POST http://localhost:8000/api/v1/llm/initialize

# You'll see output like:
# {"initialized":true,"document_count":XX,"message":"..."}

# Wait for it to complete...
```

### Step 4.4: Test LLM (5 min)

```bash
# Test LLM health
curl http://localhost:8000/api/v1/llm/health

# Should return:
# {"ollama_available":true,"vector_store_initialized":true,"model":"tinyllama",...}

# Test a query
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What protocols are monitored?"}'

# Should return an answer!
```

### Step 4.5: Test from Your Local Machine (5 min)

**From your local computer:**

```bash
# Replace YOUR_GCP_IP with the External IP you noted earlier
export GCP_IP=YOUR_GCP_IP

# Test health
curl http://$GCP_IP:8000/api/v1/health

# Test LLM
curl http://$GCP_IP:8000/api/v1/llm/health

# Test query
curl -X POST http://$GCP_IP:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Tell me about DeFi risks"}'
```

---

## ✅ COMPLETE! You're Done!

**Your setup:**
- ✅ Backend running on GCP e2-medium
- ✅ TinyLlama installed and working
- ✅ Vector store initialized
- ✅ Everything automatic (systemd services)
- ✅ Accessible from anywhere

**URLs:**
- API: `http://YOUR_GCP_IP:8000`
- API Docs: `http://YOUR_GCP_IP:8000/docs`
- Health: `http://YOUR_GCP_IP:8000/api/v1/health`
- LLM: `http://YOUR_GCP_IP:8000/api/v1/llm/health`

---

## 📊 What You Have Now

| Component | Location | Status |
|-----------|----------|--------|
| **Backend** | GCP | ✅ Running |
| **Database** | GCP | ✅ Running |
| **TinyLlama** | GCP | ✅ Running |
| **Vector Store** | GCP | ✅ Initialized |
| **Services** | Auto-start | ✅ Configured |

**Monthly Cost:** Uses your $300 GCP credit (~$24/month for e2-medium)

---

## 🔧 Management Commands

**View backend logs:**
```bash
sudo journalctl -u defi-backend -f
```

**View Ollama logs:**
```bash
sudo journalctl -u ollama -f
```

**Restart backend:**
```bash
sudo systemctl restart defi-backend
```

**Restart Ollama:**
```bash
sudo systemctl restart ollama
```

**Update code:**
```bash
cd ~/defi-project
git pull
sudo systemctl restart defi-backend
```

**Refresh vector store (after data updates):**
```bash
curl -X POST http://localhost:8000/api/v1/llm/refresh
```

---

## 🎯 Next Steps

1. **Deploy Frontend** to Vercel/Netlify (free)
2. **Add custom domain** (optional)
3. **Setup monitoring** (GCP Cloud Monitoring - free tier)
4. **Enable HTTPS** (Let's Encrypt - free)

---

## 💡 TinyLlama Performance

**What TinyLlama is good at:**
- ✅ Basic Q&A
- ✅ Protocol information retrieval
- ✅ Simple risk analysis
- ✅ Fast responses (2-3x faster than Llama3)

**Limitations:**
- ❌ Complex reasoning
- ❌ Long-form content
- ❌ Code generation

**If you need better quality later:**
- Upgrade to e2-standard-2 (8GB RAM)
- Install Mistral or Llama3
- Still within your $300 credit!

---

**Ready to start? Begin with Step 1.1!** 🚀

