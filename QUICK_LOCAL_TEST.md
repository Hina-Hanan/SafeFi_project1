# ⚡ Quick Local Test (5 Minutes)

## Fastest Way to Test Your Setup Locally

**Assumes you already have:**
- PostgreSQL installed
- Python installed
- Node.js installed

---

## 🚀 3 Commands to Start Everything

### Step 1: Start Backend (Window 1)

```powershell
cd backend

# Create .env if doesn't exist
@"
DATABASE_URL=postgresql+psycopg2://defi_user:defi_pass@localhost:5432/defi_risk_assessment
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
ENVIRONMENT=development
"@ | Out-File -FilePath .env -Encoding utf8

# Activate venv and start
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### Step 2: Start Frontend (Window 2)

```powershell
cd frontend

# Create .env.local if doesn't exist
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local

# Start
npm run dev
```

---

### Step 3: Open Browser

```
http://localhost:5173
```

---

## ✅ Quick Tests

**Test 1: Backend**
```powershell
curl http://localhost:8000/api/v1/health
```
Expected: `{"status":"ok",...}`

**Test 2: Frontend**
- Open: http://localhost:5173
- Should see dashboard

**Test 3: Data Flow**
- Dashboard should show protocol cards
- If no data: Run seed script first

---

## 🔧 If No Data

**Seed database:**

```powershell
# In backend directory with venv activated
python scripts/seed_real_protocols.py
```

Or:

```powershell
python scripts/generate_realistic_data.py
```

Then refresh browser.

---

## 🛑 Stop Everything

**Press `Ctrl+C` in each PowerShell window**

---

## 🎯 Next Steps

**If local test works:**
- ✅ Your code is good
- ✅ Ready for deployment
- ✅ Proceed with `START_HERE.md`

**If local test fails:**
- See `LOCAL_TESTING_GUIDE.md` for detailed troubleshooting
- Check logs in PowerShell windows
- Verify PostgreSQL is running

---

**That's it! 5 minutes to verify everything works locally.** ⚡

