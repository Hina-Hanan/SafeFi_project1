# Test Email Subscription - PowerShell Script
# Usage: .\test-subscribe.ps1

Write-Host "=== Email Alerts Subscription Test ===" -ForegroundColor Cyan
Write-Host ""

# Create request body
$requestBody = @{
    email = "hinahanan003@gmail.com"
    high_risk_threshold = 60.0
    medium_risk_threshold = 35.0
    notify_on_high = $true
    notify_on_medium = $true
}

# Convert to JSON
$jsonBody = $requestBody | ConvertTo-Json

Write-Host "Sending subscription request..." -ForegroundColor Yellow
Write-Host "Email: $($requestBody.email)" -ForegroundColor Gray
Write-Host "High Threshold: $($requestBody.high_risk_threshold)%" -ForegroundColor Gray
Write-Host "Medium Threshold: $($requestBody.medium_risk_threshold)%" -ForegroundColor Gray
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/email-alerts/subscribe" `
        -Method POST `
        -ContentType "application/json" `
        -Body $jsonBody
    
    Write-Host "✅ Success!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Response:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 5
    Write-Host ""
    
} catch {
    Write-Host "❌ Error occurred:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    
    if ($_.ErrorDetails.Message) {
        Write-Host "Details:" -ForegroundColor Red
        Write-Host $_.ErrorDetails.Message -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan

