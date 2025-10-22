# Complete VM Setup Guide - From Start to Running Backend

## Step 1: Start VM and Connect via SSH-in-Browser

1. Go to GCP Console → Compute Engine → VM instances
2. Click **Start** on your `defi-backend-vm`
3. Wait for status to show **Running** (green checkmark)
4. Click **SSH** → **Open in browser window**

---

## Step 2: Verify Disk Space (Should be 40GB)

```bash
df -h
```

Expected output: `/dev/sda1` should show ~40GB total

If it still shows 10GB, resize the filesystem:
```bash
sudo growpart /dev/sda 1
sudo resize2fs /dev/sda1
df -h  # Verify it now shows 40GB
```

---

## Step 3: Switch to postgres User

```bash
sudo su - postgres
cd ~
```

---

## Step 4: Clone/Update Project Repository

```bash
# If project doesn't exist, clone it
if [ ! -d "SafeFi_project1" ]; then
  git clone https://github.com/YOUR_USERNAME/SafeFi_project1.git
  cd SafeFi_project1
else
  cd SafeFi_project1
  git pull origin main
fi

cd backend
```

---

## Step 5: Create and Activate Virtual Environment

```bash
# Remove old venv if exists
rm -rf venv

# Create fresh virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

---

## Step 6: Install Dependencies in Stages

### Stage 1: Core Web Framework (Fast, ~50MB)
```bash
pip install fastapi==0.115.0 uvicorn[standard]==0.30.6 python-multipart==0.0.12
```

### Stage 2: Database (Fast, ~20MB)
```bash
pip install sqlalchemy==2.0.34 psycopg2-binary==2.9.9
```

### Stage 3: Data Validation (Fast, ~10MB)
```bash
pip install pydantic==2.9.2 email-validator==2.1.0
```

### Stage 4: HTTP & Config (Fast, ~15MB)
```bash
pip install httpx==0.27.2 python-dotenv==1.0.1
```

### Stage 5: ML Core (Medium, ~200MB)
```bash
pip install numpy==2.1.2 pandas==2.2.3 scikit-learn==1.5.2 joblib==1.4.2
```

### Stage 6: ML Models (Large, ~400MB)
```bash
pip install xgboost==2.1.1 lightgbm==4.5.0 catboost==1.2.7
```

### Stage 7: MLflow (Medium, ~100MB)
```bash
pip install mlflow==2.16.2
```

### Stage 8: Anomaly Detection (Medium, ~150MB)
```bash
pip install pyod==2.0.2 hdbscan==0.8.40 shap==0.45.1 eli5==0.13.0 imbalanced-learn==0.12.4
```

### Stage 9: Rate Limiting (Fast, ~5MB)
```bash
pip install aiolimiter==1.1.0 ratelimit==2.2.1
```

### Stage 10: LLM & RAG (Large, ~300MB - SKIP IF LOW ON SPACE)
```bash
pip install langchain==0.1.20 langchain-community==0.0.38 langchain-core==0.1.52
```

### Stage 11: Vector Store (Medium, ~100MB - SKIP IF LOW ON SPACE)
```bash
pip install chromadb==0.4.24 faiss-cpu==1.8.0
```

### Stage 12: Document Processing (Fast, ~20MB)
```bash
pip install pypdf==4.2.0 python-docx==1.1.0
```

**Check space after each stage:**
```bash
df -h
pip cache purge  # Clean cache if space is tight
```

---

## Step 7: Set Environment Variables

```bash
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://defi_user:SecurePassword2025!@localhost:5432/defi_risk_assessment

# Database Pool Configuration
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_RECYCLE=1800
DB_ISOLATION_LEVEL=READ COMMITTED

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Logging
LOG_LEVEL=INFO

# MLflow
MLFLOW_TRACKING_URI=file:///var/lib/postgresql/mlruns

# Ollama Configuration (if using LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
OLLAMA_TEMPERATURE=0.7
OLLAMA_EMBEDDING_MODEL=all-minilm
OLLAMA_TIMEOUT=120

# RAG Configuration
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_TOP_K=5
VECTOR_STORE_PATH=/var/lib/postgresql/vectorstore

# API Keys
COINGECKO_API_KEY=CG-Y27jCPKqZ28dwWuBhYjEKvGZ
ETHERSCAN_API_KEY=DTEVPVQQ2UMWI45Q4S9I2Z31E5GJTT6SN7
DEFI_LLAMA_API_KEY=not_required
ALCHEMY_API_KEY=ld2yI48GDg8mltMJVOC1o

# CoinGecko Rate Limiting
COINGECKO_MIN_INTERVAL_SEC=0.1

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Environment
ENVIRONMENT=production

# Email Alerts (configure with your credentials)
EMAIL_ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
ALERT_SENDER_EMAIL=your-email@gmail.com
ALERT_SENDER_PASSWORD=your-app-password
ALERT_RECIPIENT_EMAIL=your-email@gmail.com
EOF

# Verify .env file
cat .env
```

---

## Step 8: Set PYTHONPATH

```bash
export PYTHONPATH=/var/lib/postgresql/SafeFi_project1/backend:$PYTHONPATH
echo 'export PYTHONPATH=/var/lib/postgresql/SafeFi_project1/backend:$PYTHONPATH' >> ~/.bashrc
```

---

## Step 9: Setup Database

### A. Add Uppercase Enum Values
```bash
psql -d defi_risk_assessment <<'SQL'
-- Add uppercase protocol categories
ALTER TYPE protocol_category ADD VALUE IF NOT EXISTS 'DEX';
ALTER TYPE protocol_category ADD VALUE IF NOT EXISTS 'LENDING';
ALTER TYPE protocol_category ADD VALUE IF NOT EXISTS 'DERIVATIVES';
ALTER TYPE protocol_category ADD VALUE IF NOT EXISTS 'YIELD';
ALTER TYPE protocol_category ADD VALUE IF NOT EXISTS 'STAKING';
ALTER TYPE protocol_category ADD VALUE IF NOT EXISTS 'BRIDGE';
ALTER TYPE protocol_category ADD VALUE IF NOT EXISTS 'OTHER';

-- Add uppercase risk levels
ALTER TYPE risk_level ADD VALUE IF NOT EXISTS 'LOW';
ALTER TYPE risk_level ADD VALUE IF NOT EXISTS 'MEDIUM';
ALTER TYPE risk_level ADD VALUE IF NOT EXISTS 'HIGH';
SQL
```

### B. Verify Tables Exist
```bash
psql -d defi_risk_assessment -c "\dt"
```

If no tables, create them:
```bash
cd ~/SafeFi_project1/backend
source venv/bin/activate
python -c "from app.database.models import Base; from app.database.connection import ENGINE; Base.metadata.create_all(ENGINE); print('✅ Tables created')"
```

---

## Step 10: Seed Initial Data

```bash
cd ~/SafeFi_project1/backend
source venv/bin/activate
export PYTHONPATH=$PWD:$PYTHONPATH

# Seed protocols
python scripts/seed_data.py

# Generate realistic data
python scripts/generate_realistic_data.py

# Generate 7-day history
python scripts/generate_7day_history.py

# Verify data
psql -d defi_risk_assessment -c "SELECT COUNT(*) FROM protocols;"
psql -d defi_risk_assessment -c "SELECT COUNT(*) FROM protocol_metrics;"
psql -d defi_risk_assessment -c "SELECT COUNT(*) FROM risk_scores;"
```

---

## Step 11: Install and Setup Ollama (LLM Service) - OPTIONAL

**Note:** This step is optional. Skip if you don't need LLM/AI Assistant features or are low on disk space.

### A. Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

### B. Download TinyLlama Model (Small, ~637MB)

```bash
# Pull the model (this will take a few minutes)
ollama pull tinyllama

# Verify model is downloaded
ollama list
```

**Alternative Models:**
- `tinyllama` - Smallest (637MB) - Recommended for limited resources
- `llama3.2:1b` - Small (1.3GB) - Better quality
- `phi3:mini` - Medium (2.3GB) - Good balance
- `llama3.2:3b` - Large (2GB) - Best quality but needs more RAM

### C. Start Ollama Service

```bash
# Start Ollama in background
nohup ollama serve > ~/ollama.log 2>&1 &

# Wait a moment for it to start
sleep 5

# Test Ollama is running
curl http://localhost:11434/api/version
```

Expected output: `{"version":"0.x.x"}`

### D. Test the Model

```bash
# Quick test
ollama run tinyllama "What is DeFi?" --verbose
```

Press `Ctrl+D` to exit the chat.

### E. Install LLM Dependencies in Python Environment

```bash
cd ~/SafeFi_project1/backend
source venv/bin/activate

# Install LLM/RAG packages (if not already installed)
pip install langchain==0.1.20 langchain-community==0.0.38 langchain-core==0.1.52

# Install sentence transformers for embeddings (optional, large ~500MB)
# pip install sentence-transformers==2.7.0

# Install vector stores
pip install chromadb==0.4.24 faiss-cpu==1.8.0

# Install document processors
pip install pypdf==4.2.0 python-docx==1.1.0
```

### F. Update .env File with Ollama Configuration

```bash
# Add/update these lines in .env
cat >> .env << 'EOF'

# Ollama/LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
OLLAMA_TEMPERATURE=0.7
OLLAMA_EMBEDDING_MODEL=all-minilm
OLLAMA_TIMEOUT=120

# RAG Configuration
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_TOP_K=5
VECTOR_STORE_PATH=/var/lib/postgresql/vectorstore
EOF
```

### G. Initialize Vector Store (Knowledge Base)

```bash
cd ~/SafeFi_project1/backend
source venv/bin/activate
export PYTHONPATH=$PWD:$PYTHONPATH

# Initialize the vector store with documents
python scripts/initialize_vector_store.py 2>/dev/null || echo "Vector store will initialize on first backend startup"
```

### H. Verify LLM Setup

```bash
# Test Ollama is accessible
curl http://localhost:11434/api/tags

# Test with a simple prompt
curl http://localhost:11434/api/generate -d '{
  "model": "tinyllama",
  "prompt": "What is DeFi?",
  "stream": false
}'
```

---

## Step 12: Start Backend

```bash
cd ~/SafeFi_project1/backend
source venv/bin/activate
export PYTHONPATH=$PWD:$PYTHONPATH

# Start in foreground (for testing)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Or start in background
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

# Check if running
curl http://localhost:8000/health

# Check LLM health (if Ollama is installed)
curl -v http://localhost:8000/llm/health
```

---

## Step 13: Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get protocols
curl http://localhost:8000/protocols/

# Get risk scores
curl http://localhost:8000/risk/scores/latest

# Test LLM (if Ollama is installed)
curl http://localhost:8000/llm/health

# Ask AI Assistant a question (if Ollama is installed)
curl -X POST http://localhost:8000/llm/query/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the current risk level for Uniswap?"}'
```

---

## Step 14: Setup Firewall Rules

```bash
# In GCP Console:
# 1. Go to VPC network → Firewall
# 2. Create rule: Allow TCP port 8000 from 0.0.0.0/0
# 3. Apply to your VM

# Or use gcloud command (from local machine):
gcloud compute firewall-rules create allow-backend \
  --allow tcp:8000 \
  --source-ranges 0.0.0.0/0 \
  --target-tags http-server
```

---

## Step 15: Get External IP

```bash
# In VM
curl ifconfig.me

# Or in GCP Console
# Go to Compute Engine → VM instances → External IP
```

Your backend will be accessible at: `http://EXTERNAL_IP:8000`

**Test from your local machine:**
```bash
# Replace EXTERNAL_IP with your VM's IP
curl http://EXTERNAL_IP:8000/health
```

---

## Step 16: Setup Auto-Start Services (Optional)

To automatically start Ollama and the backend when the VM reboots:

### A. Create Ollama systemd service

```bash
sudo tee /etc/systemd/system/ollama.service > /dev/null <<'EOF'
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=postgres
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama
sudo systemctl status ollama
```

### B. Create Backend systemd service

```bash
sudo tee /etc/systemd/system/defi-backend.service > /dev/null <<'EOF'
[Unit]
Description=DeFi Risk Assessment Backend
After=network.target postgresql.service ollama.service
Requires=postgresql.service

[Service]
Type=simple
User=postgres
WorkingDirectory=/var/lib/postgresql/SafeFi_project1/backend
Environment="PYTHONPATH=/var/lib/postgresql/SafeFi_project1/backend"
ExecStart=/var/lib/postgresql/SafeFi_project1/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable defi-backend
sudo systemctl start defi-backend
sudo systemctl status defi-backend
```

### C. Manage Services

```bash
# Check status
sudo systemctl status ollama
sudo systemctl status defi-backend

# View logs
sudo journalctl -u ollama -f
sudo journalctl -u defi-backend -f

# Restart services
sudo systemctl restart ollama
sudo systemctl restart defi-backend

# Stop services
sudo systemctl stop ollama
sudo systemctl stop defi-backend
```

---

## Troubleshooting

### If Disk Space Runs Out
```bash
# Check usage
df -h
du -sh ~/SafeFi_project1/backend/venv/lib/python3.11/site-packages/* | sort -hr | head -20

# Clean cache
pip cache purge
sudo apt clean
sudo apt autoremove -y

# Remove large packages if needed
pip uninstall torch torchvision torchaudio -y
```

### If Backend Won't Start
```bash
# Check logs
tail -f backend.log

# Check if port is in use
sudo netstat -tulpn | grep 8000

# Kill existing process
pkill -f uvicorn

# Restart
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### If Database Errors
```bash
# Check connection
psql -d defi_risk_assessment -c "SELECT 1;"

# Recreate tables
python -c "from app.database.models import Base; from app.database.connection import ENGINE; Base.metadata.drop_all(ENGINE); Base.metadata.create_all(ENGINE);"

# Reseed data
python scripts/seed_data.py
```

### If Ollama/LLM Not Working

```bash
# Check Ollama is running
curl http://localhost:11434/api/version

# If not running, start it
ollama serve &

# Check if model is downloaded
ollama list

# If model missing, download it
ollama pull tinyllama

# Test model directly
ollama run tinyllama "test"

# Check Ollama logs
tail -f ~/ollama.log

# Check backend can connect to Ollama
curl http://localhost:8000/api/v1/llm/health
```

### If Vector Store Issues

```bash
# Reinitialize vector store
cd ~/SafeFi_project1/backend
source venv/bin/activate
export PYTHONPATH=$PWD:$PYTHONPATH

# Remove old vector store
rm -rf /var/lib/postgresql/vectorstore

# Reinitialize
python scripts/initialize_vector_store.py

# Restart backend
pkill -f uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### If AI Assistant Shows "OFFLINE"

1. **Check Ollama is running:**
   ```bash
   curl http://localhost:11434/api/version
   ```

2. **Check vector store is initialized:**
   ```bash
   ls -la /var/lib/postgresql/vectorstore
   ```

3. **Click "Initialize Now" button in frontend**, or

4. **Reinitialize via backend:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/llm/initialize
   ```

5. **Restart backend to auto-initialize:**
   ```bash
   pkill -f uvicorn
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

---

## Success Checklist

### Core Setup
- [ ] VM started and SSH connected
- [ ] Disk shows 40GB
- [ ] Virtual environment created and activated
- [ ] All core dependencies installed
- [ ] .env file configured
- [ ] Database tables created
- [ ] Initial data seeded (20 protocols)
- [ ] Backend starts without errors
- [ ] Health endpoint returns 200 (`curl http://localhost:8000/health`)
- [ ] API endpoints work
- [ ] Firewall rules configured
- [ ] External IP accessible

### LLM Setup (Optional)
- [ ] Ollama installed
- [ ] TinyLlama model downloaded
- [ ] Ollama service running (`curl http://localhost:11434/api/version`)
- [ ] LLM dependencies installed (langchain, chromadb, faiss)
- [ ] Vector store initialized
- [ ] LLM health endpoint works (`curl http://localhost:8000/api/v1/llm/health`)
- [ ] AI Assistant responds to queries
- [ ] Auto-start services configured (optional)

### Data Verification
- [ ] 20 protocols in database (`SELECT COUNT(*) FROM protocols`)
- [ ] ~560 metrics in database (`SELECT COUNT(*) FROM protocol_metrics`)
- [ ] ~560 risk scores in database (`SELECT COUNT(*) FROM risk_scores`)
- [ ] Risk distribution looks correct (mix of low/medium/high)

---

## Quick Reference Commands

### Start Everything
```bash
# Switch to postgres user
sudo su - postgres

# Navigate to project
cd ~/SafeFi_project1/backend

# Activate venv
source venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH=$PWD:$PYTHONPATH

# Start Ollama (if installed)
nohup ollama serve > ~/ollama.log 2>&1 &

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Check Status
```bash
# Check backend
curl http://localhost:8000/health

# Check Ollama
curl http://localhost:11434/api/version

# Check LLM
curl http://localhost:8000/api/v1/llm/health

# Check database
psql -d defi_risk_assessment -c "SELECT COUNT(*) FROM protocols;"
```

### View Logs
```bash
# Backend logs (if running in background)
tail -f backend.log

# Ollama logs
tail -f ~/ollama.log

# System service logs (if using systemd)
sudo journalctl -u defi-backend -f
sudo journalctl -u ollama -f
```

---

## Next Steps

1. Deploy frontend to Cloud Storage
2. Configure CORS for frontend domain
3. Set up automated updates with Cloud Scheduler
4. Configure monitoring and alerts
5. Test full application flow

