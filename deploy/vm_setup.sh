#!/bin/bash
# VM Setup Script for DeFi Risk Assessment Backend with LLM
# This script runs on the GCP VM to set up the complete backend

set -e

echo "=========================================="
echo "DeFi Risk Assessment Backend Setup"
echo "=========================================="
echo ""

# Get user input
read -p "Enter your GitHub username: " GITHUB_USERNAME
read -p "Enter your email for SMTP (optional, press Enter to skip): " USER_EMAIL

echo ""
echo "🔧 Starting backend setup..."
echo "GitHub: $GITHUB_USERNAME"
echo "Email: ${USER_EMAIL:-'Not configured'}"
echo ""

# Update system
echo "📦 Installing system dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib git curl wget

# Setup PostgreSQL
echo "🐘 Setting up PostgreSQL..."
sudo -i -u postgres psql << 'PSQL_EOF'
CREATE USER defi_user WITH PASSWORD 'SecurePassword2025!';
CREATE DATABASE defi_risk_assessment OWNER defi_user;
GRANT ALL PRIVILEGES ON DATABASE defi_risk_assessment TO defi_user;
\q
PSQL_EOF

# Install Ollama
echo "🤖 Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Download models
echo "📥 Downloading AI models..."
ollama serve &
sleep 5
ollama pull tinyllama
ollama pull all-minilm
echo "✅ Models downloaded:"
ollama list

# Clone repository
echo "📁 Cloning repository..."
cd ~
git clone https://github.com/$GITHUB_USERNAME/main-project.git
cd main-project/backend

# Setup Python environment
echo "🐍 Setting up Python environment..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create environment configuration
echo "⚙️ Creating environment configuration..."
cat > .env << EOF
# Database
DATABASE_URL=postgresql+psycopg2://defi_user:SecurePassword2025!@localhost:5432/defi_risk_assessment

# Ollama Configuration (ENABLED)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
OLLAMA_EMBEDDING_MODEL=all-minilm
OLLAMA_TEMPERATURE=0.7
OLLAMA_TIMEOUT=120

# RAG Configuration
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_TOP_K=5
VECTOR_STORE_PATH=/home/$USER/vectorstore

# MLflow
MLFLOW_TRACKING_URI=file:///home/$USER/mlruns

# Environment
ENVIRONMENT=production

# Email Configuration
EMAIL_ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
ALERT_SENDER_EMAIL=$USER_EMAIL
ALERT_SENDER_PASSWORD=your-app-password
ALERT_RECIPIENT_EMAIL=$USER_EMAIL

# CORS
CORS_ORIGINS=http://localhost:5173,https://storage.googleapis.com
EOF

# Initialize database
echo "🗄️ Initializing database..."
source venv/bin/activate
python scripts/seed_data.py
python scripts/generate_realistic_data.py
python scripts/generate_7day_history.py

# Setup vector store
echo "🧠 Setting up vector store..."
mkdir -p ~/vectorstore
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
sleep 10
curl -X POST http://localhost:8000/api/v1/llm/initialize
pkill -f uvicorn

# Create system services
echo "🔧 Creating system services..."

# Ollama service
sudo tee /etc/systemd/system/ollama.service > /dev/null << EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=$USER
Group=$USER
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=0.0.0.0:11434"

[Install]
WantedBy=default.target
EOF

# Backend service
sudo tee /etc/systemd/system/defi-backend.service > /dev/null << EOF
[Unit]
Description=DeFi Risk Assessment Backend API
After=network.target postgresql.service ollama.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/main-project/backend
Environment="PATH=/home/$USER/main-project/backend/venv/bin"
ExecStart=/home/$USER/main-project/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Start services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable ollama defi-backend
sudo systemctl start ollama
sleep 5
sudo systemctl start defi-backend

# Test services
echo "✅ Testing services..."
sleep 10

echo "Testing Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is running"
else
    echo "❌ Ollama failed to start"
fi

echo "Testing Backend..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend failed to start"
fi

echo "Testing LLM..."
if curl -s http://localhost:8000/api/v1/llm/health > /dev/null; then
    echo "✅ LLM is working"
else
    echo "❌ LLM failed to initialize"
fi

# Get external IP
EXTERNAL_IP=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")

echo ""
echo "🎉 Setup Complete!"
echo "=========================================="
echo "Backend URL: http://$EXTERNAL_IP:8000"
echo "Health Check: http://$EXTERNAL_IP:8000/health"
echo "LLM Health: http://$EXTERNAL_IP:8000/api/v1/llm/health"
echo ""
echo "📋 Next Steps:"
echo "1. Test backend: curl http://$EXTERNAL_IP:8000/health"
echo "2. Test LLM: curl http://$EXTERNAL_IP:8000/api/v1/llm/health"
echo "3. Proceed to Phase 3: Frontend Deployment"
echo ""
echo "🔧 Service Status:"
sudo systemctl status ollama --no-pager -l
sudo systemctl status defi-backend --no-pager -l




