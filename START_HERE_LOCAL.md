# 🚀 Start Your DeFi Risk Assessment System Locally

## 🎯 Quick Start (2 Steps)

### Step 1: Start Backend

**Option A: Double-click this file (Easiest)**
```
START_BACKEND_SIMPLE.bat
```

**Option B: Manual PowerShell**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Wait until you see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

✅ Backend ready at: **http://localhost:8000**

---

### Step 2: Start Frontend (New PowerShell Window)

```powershell
cd frontend
npm run dev
```

**Wait until you see:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

✅ Frontend ready at: **http://localhost:5173**

---

## 🎨 Open Your App

**Main App**: http://localhost:5173

**Backend API Docs**: http://localhost:8000/docs

---

## 🛑 Common Issues

### Issue 1: "This site can't be reached" 

**Cause:** Backend not running

**Fix:** 
1. Open PowerShell
2. Run: `cd backend`
3. Run: `.\venv\Scripts\Activate.ps1`
4. Run: `python -m uvicorn app.main:app --reload --port 8000`

### Issue 2: "Cannot be loaded because running scripts is disabled"

**Cause:** PowerShell execution policy

**Fix:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 3: "Port already in use"

**Cause:** Another app is using port 8000 or 5173

**Fix:**
```powershell
# Find what's using the port
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <PID_NUMBER> /F
```

Or use different ports:
```powershell
# Backend on port 8001
python -m uvicorn app.main:app --reload --port 8001

# Frontend on port 5174
npm run dev -- --port 5174
```

### Issue 4: Dependencies not installed

**Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Frontend:**
```powershell
cd frontend
npm install
```

---

## 📝 Full Startup Sequence

### Terminal 1 (Backend):
```powershell
# Navigate to backend
cd C:\Users\hinah\main-project\backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Keep this terminal open!**

### Terminal 2 (Frontend):
```powershell
# Navigate to frontend
cd C:\Users\hinah\main-project\frontend

# Start frontend dev server
npm run dev
```

**Keep this terminal open too!**

---

## ✅ Verify Everything Works

1. **Backend Health Check**
   - Open: http://localhost:8000/api/v1/health
   - Should show: `{"status": "healthy", ...}`

2. **Backend API Docs**
   - Open: http://localhost:8000/docs
   - Should show: Swagger UI with API endpoints

3. **Frontend App**
   - Open: http://localhost:5173
   - Should show: Dark theme DeFi Risk Assessment dashboard

---

## 🎯 What You Should See

### Backend Terminal:
```
INFO:     Will watch for changes in these directories: ['C:\\Users\\hinah\\main-project\\backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [67890]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Frontend Terminal:
```
  VITE v5.4.10  ready in 1234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### Browser (http://localhost:5173):
- ✅ Pure black background
- ✅ White text
- ✅ Risk metrics cards
- ✅ Protocol heatmap
- ✅ Green/Orange/Red risk colors
- ✅ No connection errors

---

## 🔄 To Stop the Servers

In each terminal, press: **Ctrl + C**

---

## 🗄️ Database Setup (Optional)

If you need to initialize the database with sample data:

```powershell
cd backend
.\venv\Scripts\Activate.ps1

# Initialize database
python scripts/init_db.py

# Seed with real protocols
python scripts/seed_real_protocols.py

# Generate 7-day history
python scripts/generate_7day_history.py
```

---

## 📊 Available Endpoints

### Backend API:

| Endpoint | Description |
|----------|-------------|
| `GET /` | API root |
| `GET /health` | Health check |
| `GET /docs` | API documentation |
| `GET /api/v1/health` | Detailed health info |
| `GET /api/v1/protocols` | List all protocols |
| `GET /api/v1/protocols/{id}/risk` | Protocol risk details |
| `GET /api/v1/risk/summary` | Risk summary |

---

## 🎨 Frontend Features

### Tabs:
1. **🔥 Risk Heatmap** - Protocol risk cards
2. **📊 7-Day Analysis** - Risk trends
3. **💼 Portfolio** - Your portfolio
4. **🤖 AI Assistant** - Ask questions (if LLM is set up)

---

## 🐛 Debugging

### See backend logs:
Backend terminal shows all API requests and errors in real-time.

### See frontend errors:
1. Open browser console (F12)
2. Check Console tab for errors
3. Check Network tab for failed API calls

### Test backend manually:
```powershell
curl http://localhost:8000/api/v1/health
```

Or open in browser: http://localhost:8000/api/v1/health

---

## 📚 Need More Help?

- **Backend Issues**: See `BACKEND_TROUBLESHOOTING.md`
- **Frontend Issues**: Check browser console (F12)
- **API Reference**: http://localhost:8000/docs

---

## ✅ Success Checklist

- [ ] Backend running (Terminal 1 shows "Application startup complete")
- [ ] Frontend running (Terminal 2 shows "ready in xxx ms")
- [ ] http://localhost:8000 accessible
- [ ] http://localhost:8000/docs shows API docs
- [ ] http://localhost:5173 shows dark dashboard
- [ ] No connection errors in browser

**If all checked, you're good to go!** 🎉

---

## 🎯 Quick Commands Reference

```powershell
# Start Backend
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --port 8000

# Start Frontend
cd frontend
npm run dev

# Check Backend Health
curl http://localhost:8000/api/v1/health

# Stop Servers
# Press Ctrl+C in each terminal
```

---

**Enjoy your DeFi Risk Assessment System!** 🚀🌙

