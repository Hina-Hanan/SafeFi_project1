# 🔧 Backend Troubleshooting Guide

## Error: "This site can't be reached - ERR_CONNECTION_REFUSED"

This means your backend server is not running. Follow these steps:

---

## ✅ Solution 1: Use the Simple Batch File (Easiest)

**Just double-click this file:**
```
START_BACKEND_SIMPLE.bat
```

It will:
1. Activate the virtual environment
2. Start the backend server
3. Show you the server output

**Then open:** http://localhost:8000 in your browser

---

## ✅ Solution 2: Manual Steps

### Step 1: Open PowerShell in the project root

### Step 2: Navigate to backend
```powershell
cd backend
```

### Step 3: Activate virtual environment
```powershell
.\venv\Scripts\Activate.ps1
```

**If you get an error about execution policy:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

### Step 4: Check if Python works
```powershell
python --version
```

Should show: Python 3.11.x or similar

### Step 5: Install dependencies (if needed)
```powershell
pip install -r requirements.txt
```

### Step 6: Start the backend
```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 7: Test
Open browser: http://localhost:8000

---

## ✅ Solution 3: Check What's Wrong

### Check 1: Is Python installed?
```powershell
python --version
```

If not, install Python 3.11+ from: https://www.python.org/downloads/

### Check 2: Is the virtual environment created?
```powershell
dir backend\venv
```

If not, create it:
```powershell
cd backend
python -m venv venv
```

### Check 3: Are dependencies installed?
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip list
```

Should show: fastapi, uvicorn, sqlalchemy, etc.

If not:
```powershell
pip install -r requirements.txt
```

### Check 4: Is the database configured?
The app uses SQLite by default if no PostgreSQL is configured, so this shouldn't be an issue.

### Check 5: Is port 8000 already in use?
```powershell
netstat -ano | findstr :8000
```

If something is using port 8000, kill it:
```powershell
taskkill /PID <PID_NUMBER> /F
```

Or use a different port:
```powershell
python -m uvicorn app.main:app --reload --port 8001
```

---

## ✅ Solution 4: Common Errors

### Error: "venv\Scripts\Activate.ps1 cannot be loaded"

**Fix:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: "No module named 'app'"

**Fix:** Make sure you're in the `backend` directory:
```powershell
cd backend
python -m uvicorn app.main:app --reload
```

### Error: "uvicorn: command not found"

**Fix:** Install uvicorn:
```powershell
pip install uvicorn
```

Or use the full Python module syntax:
```powershell
python -m uvicorn app.main:app --reload
```

### Error: Database connection issues

The app should work without a database initially. But if you need to set up the database:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python scripts/init_db.py
```

---

## ✅ Quick Test Checklist

1. [ ] PowerShell open in `backend` directory
2. [ ] Virtual environment activated (see `(venv)` in prompt)
3. [ ] Python 3.11+ installed (`python --version`)
4. [ ] Dependencies installed (`pip list`)
5. [ ] Backend running (`python -m uvicorn app.main:app --reload`)
6. [ ] Can access http://localhost:8000

---

## 🎯 Expected Output When Backend Starts

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXXX] using StatReload
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

If you see this, the backend is running! ✅

---

## 🔍 Still Not Working?

### Check the actual error message

When you run the backend command, look at the error output. Common issues:

1. **Import Error** - Missing dependencies
   - Fix: `pip install -r requirements.txt`

2. **Port already in use** - Another process is using port 8000
   - Fix: Kill the other process or use a different port

3. **Permission denied** - Can't bind to the port
   - Fix: Run as administrator or use port > 1024

4. **Database connection error** - Can't connect to PostgreSQL
   - Fix: The app should fall back to SQLite, but check your `.env` file

---

## 📝 Get Help

If you're still stuck, run this command and share the output:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --log-level debug 2>&1 | Tee-Object -FilePath error.log
```

This will save all output to `error.log` which you can review.

---

## ✅ Success!

When the backend is running:

1. **API Root**: http://localhost:8000
2. **API Docs**: http://localhost:8000/docs
3. **Health Check**: http://localhost:8000/api/v1/health

Then start your frontend:
```powershell
cd frontend
npm run dev
```

Frontend will be at: http://localhost:5173

---

**Good luck!** 🚀

