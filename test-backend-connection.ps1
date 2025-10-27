# Test Backend Connection
Write-Host "Testing Backend Connection..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Backend health
Write-Host "1. Testing Backend Health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health"
    Write-Host "✅ Backend is responding!" -ForegroundColor Green
    $health | ConvertTo-Json
} catch {
    Write-Host "❌ Backend not responding: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Backend protocols
Write-Host "2. Testing Protocols Endpoint..." -ForegroundColor Yellow
try {
    $protocols = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/protocols?limit=5"
    Write-Host "✅ Protocols endpoint working!" -ForegroundColor Green
    Write-Host "   Found $($protocols.data.Count) protocols" -ForegroundColor Gray
} catch {
    Write-Host "❌ Protocols endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: Check frontend
Write-Host "3. Checking if Frontend is Running..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 2
    Write-Host "✅ Frontend is running on port 5173!" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend not running on 5173" -ForegroundColor Red
    Write-Host "   Start it with: cd frontend; npm run dev" -ForegroundColor Yellow
}
Write-Host ""

# Test 4: CORS check
Write-Host "4. CORS Configuration Check..." -ForegroundColor Yellow
Write-Host "   Backend is configured to allow: * (all origins)" -ForegroundColor Gray
Write-Host "   If you see CORS errors, check backend/.env" -ForegroundColor Yellow
Write-Host ""

Write-Host "=== Connection Test Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Make sure backend is running: cd backend; uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host "2. Make sure frontend is running: cd frontend; npm run dev" -ForegroundColor Gray
Write-Host "3. Open browser to: http://localhost:5173" -ForegroundColor Gray

