# Frontend-Backend Connection Guide

## ✅ Status Check

### Backend Status
- ✅ Backend is running on `http://localhost:8000`
- ✅ Health endpoint working: `http://localhost:8000/health`
- ✅ Protocols endpoint working: `http://localhost:8000/protocols`
- ✅ Scheduler is running and updating data every 15-30 minutes

### Frontend Status
- ✅ Frontend is running on `http://localhost:5173`
- ✅ API configuration points to `http://127.0.0.1:8000`

## Connection Issues? Check These:

### 1. Both Servers Running?

**Backend:**
```powershell
# Should see output like:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# ✅ Automated scheduler started (15-30 minute intervals)
```

**Frontend:**
```powershell
# Should see:
#  VITE v5.x.x  ready in xxx ms
#  ➜  Local:   http://localhost:5173/
```

### 2. CORS Issues?

Backend already allows all origins (`*`), but if you see CORS errors, add to `backend/.env`:

```bash
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Then restart backend.

### 3. API Path Issues?

The frontend calls `/protocols` but the full URL is:
```
http://localhost:8000/protocols
```

NOT:
```
http://localhost:8000/api/v1/protocols  ❌
```

This has been fixed in `frontend/src/services/api.ts`.

### 4. Test the Connection

Run the test script:
```powershell
.\test-backend-connection.ps1
```

Or manually test:
```powershell
# Test backend health
Invoke-RestMethod http://localhost:8000/health

# Test protocols endpoint
Invoke-RestMethod http://localhost:8000/protocols?limit=3

# Test scheduler status  
Invoke-RestMethod http://localhost:8000/monitoring/scheduler/status
```

### 5. Browser DevTools Check

Open browser DevTools (F12) and check:

**Console Tab:**
- Look for error messages
- Look for successful API calls

**Network Tab:**
- Look for failed requests (red)
- Check if requests go to `http://localhost:8000`

**Common errors:**
- `ERR_CONNECTION_REFUSED` → Backend not running
- `ERR_BLOCKED_BY_CORS` → CORS configuration issue
- `404 Not Found` → Wrong API path

## Quick Fixes

### If Frontend shows "No protocols":

1. **Check backend is running:**
   ```powershell
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Refresh frontend** (Ctrl+F5 to hard refresh)

3. **Check browser console** for errors

### If CORS errors:

Add to `backend/.env`:
```bash
CORS_ORIGINS=http://localhost:5173
```

Restart backend.

### If 404 errors:

Make sure frontend is calling the right paths:
- ✅ `/protocols` (not `/api/v1/protocols`)
- ✅ `/health` (not `/api/v1/health`)

## Summary

✅ **Backend:** Working perfectly on port 8000  
✅ **Frontend:** Should work on port 5173  
✅ **API Paths:** Fixed in api.ts  
✅ **CORS:** Configured to allow all origins  

**Next step:** Open browser to `http://localhost:5173` and check if data loads!

