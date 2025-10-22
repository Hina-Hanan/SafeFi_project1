<!-- 4e1cfa07-72e9-4c4f-ac01-4b27dccd69ef 40a3d6bc-0fb0-4496-82a3-48b3ed2e71b2 -->
# GCP Deployment with LLM Enabled - Complete Guide

## Budget Analysis (90 days with $300 credit)

**Monthly Cost with LLM: ~$25-30 USD (₹2,075-2,490)**

- Compute Engine e2-medium: ~$24/month (for Ollama + TinyLlama)
- Cloud Storage (frontend): ~$0.50/month
- Cloud Scheduler: ~$0.30/month
- Egress (data transfer): ~$1/month
- **Total: ~$26/month × 3 = $78 for 90 days**
- **Remaining credit: $222 (74% unused)**

**LLM Configuration:**

- Model: TinyLlama (1.1GB - lightweight and fast)
- Embedding: all-minilm (small, efficient)
- Instance: e2-medium (2 vCPU, 4GB RAM - minimum for Ollama)
- Cost impact: +$12/month vs e2-small, but enables full AI features

---

## Phase 1: GCP Account & Project Setup (15 minutes)

### Step 1.1: Create GCP Account

1. Go to: https://console.cloud.google.com
2. Sign in with Google account
3. Click "Get started for free"
4. Enter credit card (required for verification, won't charge)
5. Select country: India
6. Agree to terms
7. **Verify $300 credit appears** in billing dashboard

### Step 1.2: Create Project

1. Click "Select a project" → "NEW PROJECT"
2. Name: `defi-risk-assessment`
3. Organization: No organization
4. Click "CREATE" → Wait 30 seconds
5. Select the project from dropdown

### Step 1.3: Enable APIs

Enable these APIs (search bar → click Enable):

- Compute Engine API (wait 1 min)
- Cloud Storage API (wait 30 sec)
- Cloud Scheduler API (wait 30 sec)
- Cloud Build API (wait 30 sec)

---

## Phase 2: Backend VM with LLM (60 minutes)

### Step 2.1: Create VM Instance

1. **Compute Engine** → **VM instances** → **CREATE INSTANCE**

2. Basic configuration:
   ```
   Name: defi-backend-vm
   Region: us-central1 (Iowa)
   Zone: us-central1-a
   ```

3. **Machine configuration (IMPORTANT for LLM):**
   ```
   Series: E2
   Machine type: e2-medium (2 vCPU, 4 GB memory)
   ```


**Note:** e2-medium required for Ollama. Do NOT use e2-small.

4. **Boot disk:**

   - Click "CHANGE"
   - OS: Ubuntu
   - Version: Ubuntu 22.04 LTS
   - Type: Standard persistent disk
   - Size: **40 GB** (increased for Ollama models)
   - Click "SELECT"

5. **Firewall:**

   - ✅ Allow HTTP traffic
   - ✅ Allow HTTPS traffic

6. Click **"CREATE"** → Wait 2-3 minutes
7. **Copy the External IP** (e.g., 34.123.45.67)

### Step 2.2: Configure Firewall

1. **VPC network** → **Firewall** → **CREATE FIREWALL RULE**
2. Settings:
   ```
   Name: allow-backend-api
   Network: default
   Direction: Ingress
   Action: Allow
   Targets: All instances in the network
   Source IPv4 ranges: 0.0.0.0/0
   Protocols and ports: TCP → 8000
   ```

3. Click **"CREATE"**

### Step 2.3: Connect via SSH

1. **VM instances** → Find `defi-backend-vm`
2. Click **"SSH"** button
3. Wait for browser terminal to open (15-30 sec)
4. You'll see: `yourname@defi-backend-vm:~$`

### Step 2.4: Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Git and tools
sudo apt install -y git curl wget
```

**Time: 5-8 minutes**

### Step 2.5: Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version

# Start Ollama service
ollama serve &

# Wait 5 seconds, then pull TinyLlama
sleep 5
ollama pull tinyllama

# Pull embedding model
ollama pull all-minilm

# Verify models
ollama list
# Should show: tinyllama and all-minilm
```

**Time: 3-5 minutes (TinyLlama is only 1.1GB)**

### Step 2.6: Configure Ollama as Service

```bash
# Create systemd service for Ollama
sudo tee /etc/systemd/system/ollama.service > /dev/null << 'EOF'
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=YOUR_USERNAME
Group=YOUR_USERNAME
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=0.0.0.0:11434"

[Install]
WantedBy=default.target
EOF

# Replace YOUR_USERNAME with actual username
sudo sed -i "s/YOUR_USERNAME/$USER/g" /etc/systemd/system/ollama.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama

# Check status
sudo systemctl status ollama
# Should show "Active: active (running)"
```

### Step 2.7: Configure PostgreSQL

```bash
# Switch to postgres user
sudo -i -u postgres

# Create database and user
psql << EOF
CREATE USER defi_user WITH PASSWORD 'SecurePassword2025!';
CREATE DATABASE defi_risk_assessment OWNER defi_user;
GRANT ALL PRIVILEGES ON DATABASE defi_risk_assessment TO defi_user;
\q
EOF

exit

# Test connection
psql -U defi_user -d defi_risk_assessment -h localhost -W
# Password: SecurePassword2025!
# Type \q to exit
```

### Step 2.8: Clone Repository

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/main-project.git
cd main-project/backend
ls -la
```

**Replace YOUR_USERNAME with your GitHub username**

### Step 2.9: Setup Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Time: 5-10 minutes**

### Step 2.10: Configure Environment Variables

```bash
# Create .env file with LLM enabled
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql+psycopg2://defi_user:SecurePassword2025!@localhost:5432/defi_risk_assessment

# Ollama Configuration (ENABLED)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
OLLAMA_EMBEDDING_MODEL=all-minilm
OLLAMA_TEMPERATURE=0.7
OLLAMA_TIMEOUT=120

# RAG Configuration
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_TOP_K=5
VECTOR_STORE_PATH=/home/$USER/vectorstore

# MLflow
MLFLOW_TRACKING_URI=file:///home/$USER/mlruns

# Environment
ENVIRONMENT=production

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=hinahanan2003@gmail.com
EOF

cat .env
```

### Step 2.11: Initialize Database & Data

```bash
source venv/bin/activate

# Seed protocols
python scripts/seed_data.py

# Generate initial data
python scripts/generate_realistic_data.py

# Generate 7-day history
python scripts/generate_7day_history.py
```

**Time: 2-3 minutes**

### Step 2.12: Initialize Vector Store

```bash
# Create vectorstore directory
mkdir -p ~/vectorstore

# Start backend temporarily to initialize vector store
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
sleep 10

# Initialize vector store
curl -X POST http://localhost:8000/llm/initialize

# Check status
curl http://localhost:8000/llm/health

# Should return: {"ollama_available":true,"vector_store_initialized":true}

# Stop temporary server
pkill -f uvicorn
```

### Step 2.13: Setup Backend Service

```bash
sudo tee /etc/systemd/system/defi-backend.service > /dev/null << EOF
[Unit]
Description=DeFi Risk Assessment Backend API
After=network.target postgresql.service ollama.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/main-project/backend
Environment="PATH=/home/$USER/main-project/backend/venv/bin"
ExecStart=/home/$USER/main-project/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload and start
sudo systemctl daemon-reload
sudo systemctl enable defi-backend
sudo systemctl start defi-backend

# Check status
sudo systemctl status defi-backend
```

### Step 2.14: Test LLM Functionality

```bash
# Test Ollama directly
curl http://localhost:11434/api/tags

# Test backend health
curl http://localhost:8000/health

# Test LLM health
curl http://localhost:8000/api/v1/llm/health

# Test AI chat
curl -X POST http://localhost:8000/api/v1/llm/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is DeFi risk assessment?"}'

# Should return AI response
```

---

## Phase 3: Frontend Deployment (30 minutes)

### Step 3.1: Update Frontend API URL

**On your local computer:**

Edit `frontend/src/services/api.ts`:

```typescript
const API_BASE_URL = 'http://YOUR_VM_IP:8000/api/v1';
```

Replace YOUR_VM_IP with your actual GCP VM external IP.

### Step 3.2: Build Frontend

```powershell
cd frontend
npm install
npm run build
```

Creates `dist` folder with production files.

### Step 3.3: Create Cloud Storage Bucket

1. GCP Console → **Cloud Storage** → **Buckets** → **CREATE**
2. Settings:
   ```
   Name: defi-risk-frontend-YOUR_UNIQUE_ID
   Location: Region → us-central1
   Storage class: Standard
   Access control: Fine-grained
   ```

3. Click **CREATE** → **ALLOW PUBLIC ACCESS**

### Step 3.4: Upload Frontend Files

1. Open bucket
2. **UPLOAD FILES** → Select all from `frontend/dist`
3. **UPLOAD FOLDER** → Select `frontend/dist/assets`
4. Wait for upload complete

### Step 3.5: Make Bucket Public

1. **PERMISSIONS** tab → **ADD PRINCIPAL**
2. New principals: `allUsers`
3. Role: **Storage Object Viewer**
4. **SAVE** → **ALLOW PUBLIC ACCESS**

### Step 3.6: Get Frontend URL

Click on `index.html` → Copy **Public URL**:

`https://storage.googleapis.com/defi-risk-frontend-YOUR_ID/index.html`

---

## Phase 4: CORS Configuration (10 minutes)

### Step 4.1: Update Backend CORS

SSH into VM:

```bash
cd ~/main-project/backend
source venv/bin/activate
nano app/main.py
```

Update CORS middleware:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://storage.googleapis.com",
        "http://YOUR_VM_IP:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Save and restart:

```bash
sudo systemctl restart defi-backend
```

### Step 4.2: Test Full System

1. Open frontend URL in browser
2. Test features:

   - ✅ Dashboard loads with protocols
   - ✅ Risk scores display
   - ✅ Charts render
   - ✅ **AI Assistant tab shows ONLINE**
   - ✅ **Chat with AI works**

---

## Phase 5: Automated Updates (20 minutes)

### Step 5.1: Create Update Scripts

SSH into VM:

```bash
cat > ~/update_risks.sh << 'EOF'
#!/bin/bash
cd ~/main-project/backend
source venv/bin/activate
python scripts/auto_update_risks.py >> ~/logs/risk_updates.log 2>&1
EOF

cat > ~/update_data.sh << 'EOF'
#!/bin/bash
cd ~/main-project/backend
source venv/bin/activate
python scripts/update_live_data.py >> ~/logs/data_updates.log 2>&1
EOF

chmod +x ~/update_risks.sh ~/update_data.sh
mkdir -p ~/logs
```

### Step 5.2: Add Admin Endpoints

```bash
cd ~/main-project/backend
cat > app/api/v1/admin.py << 'EOF'
from fastapi import APIRouter, BackgroundTasks
import subprocess
import logging
import os

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)

@router.post("/trigger-risk-update")
async def trigger_risk_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_script, "/home/{}/update_risks.sh".format(os.environ.get("USER", "username")))
    return {"status": "scheduled", "job": "risk_update"}

@router.post("/trigger-data-update")
async def trigger_data_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_script, "/home/{}/update_data.sh".format(os.environ.get("USER", "username")))
    return {"status": "scheduled", "job": "data_update"}

def run_script(script_path: str):
    subprocess.run([script_path], shell=False)
EOF

# Add to main router
nano app/api/router.py
# Add: from app.api.v1 import admin
# Add: api_router.include_router(admin.router, prefix="/api/v1")

sudo systemctl restart defi-backend
```

### Step 5.3: Setup Cloud Scheduler

GCP Console → **Cloud Scheduler** → **CREATE JOB**

**Job 1: Risk Updates**

```
Name: risk-updates-every-5h
Region: us-central1
Frequency: 0 */5 * * *
Timezone: Asia/Kolkata (IST)
Target: HTTP
URL: http://YOUR_VM_IP:8000/api/v1/admin/trigger-risk-update
HTTP method: POST
```

**Job 2: Data Updates**

```
Name: data-sync-every-3h
Region: us-central1
Frequency: 0 */3 * * *
Timezone: Asia/Kolkata (IST)
Target: HTTP
URL: http://YOUR_VM_IP:8000/api/v1/admin/trigger-data-update
HTTP method: POST
```

---

## Phase 6: Cost Monitoring (10 minutes)

### Step 6.1: Budget Alerts

**Billing** → **Budgets & alerts** → **CREATE BUDGET**

```
Name: 90-day-deployment-budget
Amount: $100 USD
Alerts: 50%, 75%, 90%, 100%
Email: your-email@gmail.com
```

### Step 6.2: Monitor Usage

Check weekly at: **Billing** → **Reports**

Expected costs:

- Week 1-4: ~$24-26/month
- Total 90 days: ~$75-80
- Remaining: ~$220

---

## Phase 7: Verification (15 minutes)

### Final Checklist

**Backend:**

- [ ] `curl http://YOUR_VM_IP:8000/health` returns healthy
- [ ] `curl http://YOUR_VM_IP:8000/api/v1/llm/health` shows ollama_available: true
- [ ] Ollama running: `sudo systemctl status ollama`
- [ ] Backend running: `sudo systemctl status defi-backend`

**LLM:**

- [ ] `ollama list` shows tinyllama and all-minilm
- [ ] Vector store initialized (check ~/vectorstore has files)
- [ ] Chat works: `curl -X POST http://YOUR_VM_IP:8000/api/v1/llm/chat -H "Content-Type: application/json" -d '{"message":"test"}'`

**Frontend:**

- [ ] Dashboard loads
- [ ] Protocols display
- [ ] Charts render
- [ ] AI Assistant shows ONLINE (green)
- [ ] Can chat with AI and get responses

**Automation:**

- [ ] Cloud Scheduler jobs created
- [ ] Test trigger works

---

## Troubleshooting

### Ollama Not Running

```bash
sudo systemctl status ollama
sudo journalctl -u ollama -n 50
sudo systemctl restart ollama
```

### Out of Memory

```bash
# Check memory
free -h

# If low, reduce workers in backend service
sudo nano /etc/systemd/system/defi-backend.service
# Change --workers 2 to --workers 1
sudo systemctl restart defi-backend
```

### Vector Store Fails

```bash
cd ~/main-project/backend
source venv/bin/activate
rm -rf ~/vectorstore/*
python scripts/initialize_vector_store.py
```

### AI Responses Slow

- Normal for TinyLlama on e2-medium
- First response: 10-15 seconds
- Subsequent: 5-10 seconds
- To speed up: upgrade to e2-standard-2 (adds $25/month)

---

## Summary

**Deployed:**

- ✅ Backend API with LLM (e2-medium)
- ✅ Ollama + TinyLlama (1.1GB model)
- ✅ Vector store with RAG
- ✅ PostgreSQL database
- ✅ Frontend on Cloud Storage
- ✅ Automated updates
- ✅ **Fully functional AI Assistant**

**Cost:** ~$26/month = $78 for 90 days

**Remaining Credit:** $222 (74% unused)

**URLs:**

- Frontend: `https://storage.googleapis.com/defi-risk-frontend-YOUR_ID/index.html`
- Backend: `http://YOUR_VM_IP:8000`
- Health: `http://YOUR_VM_IP:8000/health`
- LLM Health: `http://YOUR_VM_IP:8000/api/v1/llm/health`

**Key Features Enabled:**

- Real-time risk monitoring ✅
- 7-day trend analysis ✅
- Protocol heatmap ✅
- **AI-powered chat assistant ✅**
- Automated risk updates ✅
- Email alerts (if configured) ✅

You now have a fully functional DeFi Risk Assessment platform with AI capabilities, deployed on GCP, running entirely within your $300 free credit!