# 🧪 Local Testing Guide

## Test Your Backend + Frontend Locally Before Hosting

**Time: 30-40 minutes**

---

## 📋 Prerequisites

- [ ] Windows with PowerShell
- [ ] Python 3.11 installed
- [ ] Node.js 18+ installed
- [ ] PostgreSQL installed (or use Docker)
- [ ] Git installed

---

## Part 1: Backend Setup (20 min)

### Step 1.1: Install PostgreSQL Locally (10 min)

**Option A: PostgreSQL Installer (Recommended)**

1. Download: [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
2. Run installer
3. Set password: Remember this!
4. Keep default port: 5432
5. Finish installation

**Option B: Docker (if you have Docker)**

```powershell
docker run -d `
  --name defi-postgres `
  -e POSTGRES_USER=defi_user `
  -e POSTGRES_PASSWORD=defi_pass `
  -e POSTGRES_DB=defi_risk_assessment `
  -p 5432:5432 `
  postgres:15
```

---

### Step 1.2: Create Database (5 min)

**Open PowerShell:**

```powershell
# Connect to PostgreSQL
psql -U postgres

# Create user and database
CREATE USER defi_user WITH PASSWORD 'defi_pass';
CREATE DATABASE defi_risk_assessment OWNER defi_user;
GRANT ALL PRIVILEGES ON DATABASE defi_risk_assessment TO defi_user;
\q
```

---

### Step 1.3: Setup Backend (5 min)

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

### Step 1.4: Configure Backend Environment

**Create `backend/.env` file:**

```powershell
# In backend directory
notepad .env
```

**Add this content:**

```bash
# Database
DATABASE_URL=postgresql+psycopg2://defi_user:defi_pass@localhost:5432/defi_risk_assessment

# Ollama (if you want to test LLM locally)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
OLLAMA_TEMPERATURE=0.7
OLLAMA_TIMEOUT=120
OLLAMA_EMBEDDING_MODEL=all-minilm

# RAG Configuration
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_TOP_K=5
VECTOR_STORE_PATH=./data/vectorstore

# MLflow
MLFLOW_TRACKING_URI=file:///./mlruns

# Environment
ENVIRONMENT=development
```

**Save and close.**

---

### Step 1.5: Initialize Database (Optional)

**If you have seed data:**

```powershell
# Still in backend directory with venv activated

# Run migrations (if you have them)
python -m alembic upgrade head

# Seed data (if you have seed scripts)
python scripts/seed_real_protocols.py

# Or generate test data
python scripts/generate_realistic_data.py
```

---

### Step 1.6: Start Backend

```powershell
# In backend directory with venv activated
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**✅ Backend is running at: http://localhost:8000**

---

### Step 1.7: Test Backend (Keep it running!)

**Open a NEW PowerShell window:**

```powershell
# Test health
curl http://localhost:8000/api/v1/health

# Test protocols
curl http://localhost:8000/protocols

# Test API docs (open in browser)
start http://localhost:8000/docs
```

**✅ If you see data, backend is working!**

---

## Part 2: Frontend Setup (10 min)

### Step 2.1: Setup Frontend

**Open a NEW PowerShell window:**

```powershell
# Navigate to frontend
cd frontend

# Install dependencies (takes 3-5 minutes)
npm install
```

---

### Step 2.2: Configure Frontend

**Create `frontend/.env.local` file:**

```powershell
# In frontend directory
notepad .env.local
```

**Add this content:**

```bash
# Local development API URL
VITE_API_BASE_URL=http://localhost:8000
```

**Save and close.**

---

### Step 2.3: Start Frontend

```powershell
# In frontend directory
npm run dev
```

**Expected output:**
```
  VITE v4.x.x  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

**✅ Frontend is running at: http://localhost:5173**

---

### Step 2.4: Test Frontend

**Open browser:**

```
http://localhost:5173
```

**You should see:**
- ✅ Dashboard loads
- ✅ Protocol heatmap displays
- ✅ Charts render with data
- ✅ All 4 tabs work

---

## Part 3: Test AI Assistant (Optional - 20 min)

**If you want to test the AI chat locally:**

### Step 3.1: Install Ollama

```powershell
# Download and install from:
winget install Ollama.Ollama
```

### Step 3.2: Pull TinyLlama

```powershell
# Pull model (1.1GB)
ollama pull tinyllama

# Pull embedding model
ollama pull all-minilm

# Verify
ollama list
```

### Step 3.3: Start Ollama

```powershell
# Ollama should start automatically
# Or run:
ollama serve
```

### Step 3.4: Initialize Vector Store

**In a PowerShell window:**

```powershell
# Initialize RAG with your database data
curl -X POST http://localhost:8000/api/v1/llm/initialize
```

**Wait 5-10 minutes for completion.**

### Step 3.5: Test AI Assistant

**Open browser:**
```
http://localhost:5173
```

1. Click **"🤖 AI Assistant"** tab
2. Should show **"ONLINE"** status
3. Type: "What protocols are monitored?"
4. Click Send
5. **Should get a response!**

---

## ✅ Complete Local Setup

**You now have 3 services running:**

| Service | URL | PowerShell Window |
|---------|-----|-------------------|
| Backend | http://localhost:8000 | Window 1 |
| Frontend | http://localhost:5173 | Window 2 |
| Ollama (optional) | http://localhost:11434 | Auto-start |

---

## 🧪 Testing Checklist

### Backend Tests
- [ ] Health check: `curl http://localhost:8000/api/v1/health`
- [ ] Protocols: `curl http://localhost:8000/protocols`
- [ ] API docs: http://localhost:8000/docs
- [ ] Database connected (check health response)

### Frontend Tests
- [ ] Dashboard loads at http://localhost:5173
- [ ] 🔥 Risk Heatmap shows protocols
- [ ] 📊 7-Day Analysis shows charts
- [ ] 💼 Portfolio Analyzer accepts input
- [ ] No console errors (F12)

### AI Assistant Tests (Optional)
- [ ] LLM health: `curl http://localhost:8000/api/v1/llm/health`
- [ ] Vector store initialized
- [ ] Chat shows "ONLINE"
- [ ] Can send messages and get responses

---

## 🔧 Troubleshooting

### Backend won't start

**Error: Database connection failed**
```powershell
# Check PostgreSQL is running
# Windows Services → PostgreSQL

# Or restart:
# Services → PostgreSQL → Restart
```

**Error: Port 8000 already in use**
```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Error: Module not found**
```powershell
# Reinstall dependencies
pip install -r requirements.txt
```

---

### Frontend won't start

**Error: Port 5173 already in use**
```powershell
# Kill process
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

**Error: Cannot find module**
```powershell
# Reinstall dependencies
rm -rf node_modules
npm install
```

**Error: CORS error in console**
- Check backend is running
- Check backend CORS settings in `app/main.py`
- Should allow `http://localhost:5173`

---

### AI Assistant won't work

**Shows "OFFLINE"**
```powershell
# Check Ollama is running
curl http://localhost:11434

# Restart Ollama
taskkill /F /IM ollama.exe
ollama serve
```

**No response from chat**
```powershell
# Check LLM health
curl http://localhost:8000/api/v1/llm/health

# Reinitialize vector store
curl -X POST http://localhost:8000/api/v1/llm/initialize
```

---

## 💡 Development Tips

### Hot Reload

**Backend:**
- Changes auto-reload (using `--reload` flag)
- Edit Python files → saves → auto-restart

**Frontend:**
- Changes auto-refresh in browser
- Edit React files → saves → browser updates

### View Logs

**Backend logs:**
- Visible in PowerShell window running uvicorn
- Check for errors in real-time

**Frontend logs:**
- Browser console (F12)
- Check Network tab for API calls

### Database GUI

**Use pgAdmin or DBeaver to view database:**
- Host: localhost
- Port: 5432
- Database: defi_risk_assessment
- User: defi_user
- Password: defi_pass

---

## 🎯 After Local Testing Succeeds

**Once everything works locally:**

1. **Stop local services** (Ctrl+C in each window)
2. **Commit your changes** (if any)
3. **Proceed with GCP deployment** (use `START_HERE.md`)

**Why test locally first?**
- ✅ Catch bugs before deploying
- ✅ Faster development cycle
- ✅ Verify all features work
- ✅ Debug easily with logs
- ✅ No cost while testing

---

## 🚀 Quick Start Commands

**Open 2 PowerShell windows:**

**Window 1 (Backend):**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Window 2 (Frontend):**
```powershell
cd frontend
npm run dev
```

**Window 3 (Optional - Ollama):**
```powershell
ollama serve
```

**Open browser:**
```
http://localhost:5173
```

---

## 📊 Local Architecture

```
┌─────────────────────┐
│   Browser           │
│   localhost:5173    │
└──────────┬──────────┘
           │
           ↓ HTTP
┌─────────────────────┐
│   Vite Dev Server   │
│   (Frontend)        │
│   - React           │
│   - Hot reload      │
└──────────┬──────────┘
           │
           ↓ API Calls
┌─────────────────────┐
│   Uvicorn           │
│   localhost:8000    │
│   (Backend)         │
│   - FastAPI         │
│   - Auto-reload     │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│   PostgreSQL        │
│   localhost:5432    │
│   (Database)        │
└─────────────────────┘
           
           +
           
┌─────────────────────┐
│   Ollama            │
│   localhost:11434   │
│   (Optional)        │
│   - TinyLlama       │
└─────────────────────┘
```

---

## ✅ Success Criteria

**Your local setup is complete when:**

- [ ] Backend responds to health check
- [ ] Frontend loads in browser
- [ ] Protocol data displays
- [ ] Charts render correctly
- [ ] All tabs are functional
- [ ] No console errors
- [ ] (Optional) AI chat works

**Then you're ready for production deployment!**

---

**Need help? Let me know which step you're on!** 🧪

