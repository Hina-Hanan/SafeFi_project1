# Frontend Deployment Script for PowerShell
# Run this script from the project root directory

param(
    [Parameter(Mandatory=$true)]
    [string]$VM_IP,
    
    [Parameter(Mandatory=$true)]
    [string]$PROJECT_ID
)

Write-Host "=== DeFi Risk Assessment - Frontend Deployment ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create .env.production
Write-Host "Step 1: Creating .env.production with API URL..." -ForegroundColor Yellow
$envContent = "VITE_API_BASE_URL=http://${VM_IP}:8000"
$envContent | Out-File -FilePath "frontend\.env.production" -Encoding UTF8
Write-Host "✓ Created .env.production" -ForegroundColor Green
Write-Host "  API URL: http://${VM_IP}:8000" -ForegroundColor Gray
Write-Host ""

# Step 2: Build frontend
Write-Host "Step 2: Building frontend for production..." -ForegroundColor Yellow
Set-Location frontend
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Build completed successfully" -ForegroundColor Green
Set-Location ..
Write-Host ""

# Step 3: Create Cloud Storage bucket
Write-Host "Step 3: Creating Cloud Storage bucket..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$BUCKET_NAME = "safefi-frontend-${timestamp}"
Write-Host "  Bucket name: $BUCKET_NAME" -ForegroundColor Gray

gsutil mb -p $PROJECT_ID gs://$BUCKET_NAME
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to create bucket!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Bucket created" -ForegroundColor Green
Write-Host ""

# Step 4: Make bucket public
Write-Host "Step 4: Making bucket public..." -ForegroundColor Yellow
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
Write-Host "✓ Bucket is now public" -ForegroundColor Green
Write-Host ""

# Step 5: Upload files
Write-Host "Step 5: Uploading files to Cloud Storage..." -ForegroundColor Yellow
gsutil -m cp -r frontend/dist/* gs://$BUCKET_NAME/
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to upload files!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Files uploaded" -ForegroundColor Green
Write-Host ""

# Step 6: Configure website hosting
Write-Host "Step 6: Configuring website hosting..." -ForegroundColor Yellow
gsutil web set -m index.html -e index.html gs://$BUCKET_NAME
Write-Host "✓ Website hosting configured" -ForegroundColor Green
Write-Host ""

# Step 7: Display URLs
Write-Host "=== Deployment Complete! ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your application is now live!" -ForegroundColor Green
Write-Host ""
Write-Host "Backend API: http://${VM_IP}:8000" -ForegroundColor White
Write-Host "Frontend URL: https://storage.googleapis.com/${BUCKET_NAME}/index.html" -ForegroundColor White
Write-Host "API Docs: http://${VM_IP}:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update backend CORS settings (see FRONTEND_DEPLOYMENT_GUIDE.md)" -ForegroundColor Gray
Write-Host "2. Test the frontend in your browser" -ForegroundColor Gray
Write-Host "3. Configure custom domain (optional)" -ForegroundColor Gray
Write-Host ""
Write-Host "Bucket name: $BUCKET_NAME" -ForegroundColor Cyan
Write-Host "(Save this for future deployments)" -ForegroundColor Gray
Write-Host ""

# Save deployment info
$deployInfo = @"
Deployment completed: $(Get-Date)
VM IP: $VM_IP
Project ID: $PROJECT_ID
Bucket Name: $BUCKET_NAME
Frontend URL: https://storage.googleapis.com/${BUCKET_NAME}/index.html
Backend API: http://${VM_IP}:8000
"@
$deployInfo | Out-File -FilePath "deploy/last_deployment.txt" -Encoding UTF8
Write-Host "✓ Deployment info saved to deploy/last_deployment.txt" -ForegroundColor Green







