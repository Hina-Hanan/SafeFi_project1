# Create .env file with email disabled
$envContent = @"
# Database Configuration
DATABASE_URL=postgresql+psycopg2://defi_user:usersafety@localhost:5432/defi_risk_assessment

# MLflow Configuration
MLFLOW_TRACKING_URI=http://localhost:5000

# LLM Configuration (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
OLLAMA_TEMPERATURE=0.7
OLLAMA_EMBEDDING_MODEL=all-minilm
OLLAMA_TIMEOUT=120

# RAG Configuration
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_TOP_K=5
VECTOR_STORE_PATH=./data/vectorstore

# Email Alert Configuration - DISABLED (no warning will show)
EMAIL_ALERTS_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
ALERT_SENDER_EMAIL=
ALERT_SENDER_PASSWORD=

# Environment
ENVIRONMENT=development
"@

$envContent | Out-File -FilePath ".env" -Encoding utf8 -NoNewline

Write-Host "✓ .env file created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Email alerts are DISABLED (no warning will appear)" -ForegroundColor Yellow
Write-Host ""
Write-Host "To enable email alerts later:" -ForegroundColor Cyan
Write-Host "1. Get Gmail App Password from: https://myaccount.google.com/apppasswords"
Write-Host "2. Edit .env file"
Write-Host "3. Change EMAIL_ALERTS_ENABLED=true"
Write-Host "4. Add your email and password"
Write-Host "5. Restart backend"
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

