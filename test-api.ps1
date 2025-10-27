# Complete API Test Script for PowerShell
# Tests all the new monitoring endpoints

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "SafeFi API Test Suite" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Scheduler Status
Write-Host "1. Testing Scheduler Status..." -ForegroundColor Yellow
try {
    $status = Invoke-RestMethod -Uri "http://localhost:8000/monitoring/scheduler/status"
    Write-Host "✅ Scheduler is running!" -ForegroundColor Green
    Write-Host "   Update Count: $($status.update_count)" -ForegroundColor Gray
    Write-Host "   Next Run: $($status.next_scheduled_run)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Alert Statistics
Write-Host "2. Testing Alert Statistics..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "http://localhost:8000/monitoring/alerts/statistics"
    Write-Host "✅ Statistics retrieved!" -ForegroundColor Green
    Write-Host "   Active Subscribers: $($stats.subscribers.total_active)" -ForegroundColor Gray
    Write-Host "   Total Protocols: $($stats.protocols.total_active)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: Subscribe to Email Alerts
Write-Host "3. Testing Email Subscription..." -ForegroundColor Yellow
$requestBody = @{
    email = "hinahanan003@gmail.com"
    high_risk_threshold = 60.0
    medium_risk_threshold = 35.0
    notify_on_high = $true
    notify_on_medium = $true
} | ConvertTo-Json

try {
    $subscribe = Invoke-RestMethod -Uri "http://localhost:8000/email-alerts/subscribe" `
        -Method POST `
        -ContentType "application/json" `
        -Body $requestBody
    Write-Host "✅ Subscription successful!" -ForegroundColor Green
    Write-Host "   Email: $($subscribe.email)" -ForegroundColor Gray
    Write-Host "   Subscriber ID: $($subscribe.subscriber_id)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: Get Subscriber Status
Write-Host "4. Testing Subscriber Status..." -ForegroundColor Yellow
try {
    $subStatus = Invoke-RestMethod -Uri "http://localhost:8000/monitoring/alerts/subscriber/hinahanan003@gmail.com/status"
    Write-Host "✅ Subscriber status retrieved!" -ForegroundColor Green
    Write-Host "   Email: $($subStatus.subscriber_email)" -ForegroundColor Gray
    Write-Host "   High Threshold: $($subStatus.high_risk_threshold)%" -ForegroundColor Gray
    Write-Host "   Protocols Above High: $($subStatus.protocols_above_high_threshold)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Send Test Alert
Write-Host "5. Testing Test Alert (if email configured)..." -ForegroundColor Yellow
try {
    $testAlert = Invoke-RestMethod -Uri "http://localhost:8000/monitoring/alerts/test/hinahanan003@gmail.com" `
        -Method POST
    Write-Host "✅ Test alert sent!" -ForegroundColor Green
    Write-Host "   Message: $($testAlert.message)" -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Test alert failed (email may not be configured): $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host ""

# Test 6: Force Update
Write-Host "6. Testing Force Update..." -ForegroundColor Yellow
try {
    $forceUpdate = Invoke-RestMethod -Uri "http://localhost:8000/monitoring/scheduler/force-update" `
        -Method POST
    Write-Host "✅ Force update successful!" -ForegroundColor Green
    Write-Host "   Message: $($forceUpdate.message)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Test Suite Complete" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

