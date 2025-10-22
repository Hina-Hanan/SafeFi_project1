#!/bin/bash
# GCP Deployment Script - Phase 2: Backend VM with LLM
# This script sets up the backend VM with Ollama and TinyLlama

echo "=========================================="
echo "Phase 2: Backend VM with LLM Setup"
echo "=========================================="
echo ""

# Get VM details from user
read -p "Enter your GCP VM External IP: " VM_IP
read -p "Enter your GitHub username: " GITHUB_USERNAME
read -p "Enter your email for SMTP (optional): " USER_EMAIL

echo ""
echo "🔧 Starting VM setup..."
echo "VM IP: $VM_IP"
echo "GitHub: $GITHUB_USERNAME"
echo ""

# Create VM setup script
cat > vm_setup.sh << 'EOF'
#!/bin/bash
set -e

echo "📦 Installing system dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib git curl wget

echo "🐘 Setting up PostgreSQL..."
sudo -i -u postgres psql << 'PSQL_EOF'
CREATE USER defi_user WITH PASSWORD 'SecurePassword2025!';
CREATE DATABASE defi_risk_assessment OWNER defi_user;
GRANT ALL PRIVILEGES ON DATABASE defi_risk_assessment TO defi_user;
\q
PSQL_EOF

echo "🤖 Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

echo "📥 Downloading TinyLlama model..."
ollama serve &
sleep 5
ollama pull tinyllama
ollama pull all-minilm

echo "📁 Cloning repository..."
cd ~
git clone https://github.com/GITHUB_USERNAME/main-project.git
cd main-project/backend

echo "🐍 Setting up Python environment..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "⚙️ Creating environment configuration..."
cat > .env << 'ENV_EOF'
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

# Email (if provided)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=USER_EMAIL
SMTP_PASSWORD=your-app-password
EMAIL_FROM=USER_EMAIL
ENV_EOF

# Replace placeholders
sed -i "s/GITHUB_USERNAME/$GITHUB_USERNAME/g" ~/vm_setup.sh
sed -i "s/USER_EMAIL/$USER_EMAIL/g" .env

echo "🗄️ Initializing database..."
source venv/bin/activate
python scripts/seed_data.py
python scripts/generate_realistic_data.py
python scripts/generate_7day_history.py

echo "🧠 Setting up vector store..."
mkdir -p ~/vectorstore
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
sleep 10
curl -X POST http://localhost:8000/api/v1/llm/initialize
pkill -f uvicorn

echo "🔧 Creating system services..."
sudo tee /etc/systemd/system/ollama.service > /dev/null << 'OLLAMA_EOF'
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
OLLAMA_EOF

sudo tee /etc/systemd/system/defi-backend.service > /dev/null << 'BACKEND_EOF'
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
BACKEND_EOF

# Replace $USER with actual username
sudo sed -i "s/\$USER/$USER/g" /etc/systemd/system/ollama.service
sudo sed -i "s/\$USER/$USER/g" /etc/systemd/system/defi-backend.service

echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable ollama defi-backend
sudo systemctl start ollama
sleep 5
sudo systemctl start defi-backend

echo "✅ Setup complete! Testing services..."
sleep 10

echo "Testing Ollama..."
curl -s http://localhost:11434/api/tags | head -1

echo "Testing Backend..."
curl -s http://localhost:8000/health | head -1

echo "Testing LLM..."
curl -s http://localhost:8000/api/v1/llm/health | head -1

echo ""
echo "🎉 Phase 2 Complete!"
echo "Backend URL: http://$VM_IP:8000"
echo "Health Check: http://$VM_IP:8000/health"
echo "LLM Health: http://$VM_IP:8000/api/v1/llm/health"
EOF

echo "📋 INSTRUCTIONS:"
echo ""
echo "1. Go to GCP Console → Compute Engine → VM instances"
echo "2. Find your VM and click 'SSH'"
echo "3. Copy and paste this command:"
echo ""
echo "curl -fsSL https://raw.githubusercontent.com/$GITHUB_USERNAME/main-project/main/deploy/vm_setup.sh | bash"
echo ""
echo "OR upload vm_setup.sh to your VM and run:"
echo "bash vm_setup.sh"
echo ""
echo "⏱️ Expected time: 15-20 minutes"
echo "📊 Monitor progress in SSH terminal"
echo ""
echo "✅ Next: Phase 3 - Frontend Deployment"




