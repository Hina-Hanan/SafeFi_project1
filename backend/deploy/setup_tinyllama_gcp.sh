#!/bin/bash
# TinyLlama GCP Setup Script
# This script automates the complete setup on a GCP Ubuntu instance
# Estimated time: 40-60 minutes

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Progress indicator
STEP=0
TOTAL_STEPS=15

print_step() {
    STEP=$((STEP + 1))
    echo -e "${BLUE}[${STEP}/${TOTAL_STEPS}] $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ ERROR: $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

echo -e "${BLUE}=========================================="
echo "DeFi Risk Assessment + TinyLlama Setup"
echo "==========================================${NC}"
echo ""

# Check if running on Ubuntu
if [ ! -f /etc/lsb-release ]; then
    print_error "This script requires Ubuntu"
    exit 1
fi

print_step "Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_success "System updated"

print_step "Installing Python 3.11..."
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
sudo apt install -y git curl build-essential wget
python3.11 --version
print_success "Python 3.11 installed"

print_step "Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib
print_success "PostgreSQL installed"

print_step "Configuring PostgreSQL..."
DB_PASSWORD=$(openssl rand -base64 20)
echo "$DB_PASSWORD" > ~/db_password.txt
chmod 600 ~/db_password.txt

sudo -u postgres psql << EOF
CREATE USER defi_user WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE defi_risk_assessment OWNER defi_user;
GRANT ALL PRIVILEGES ON DATABASE defi_risk_assessment TO defi_user;
\q
EOF

print_success "PostgreSQL configured"
print_warning "Database password saved to: ~/db_password.txt"

print_step "Cloning repository..."
read -p "Enter your GitHub repository URL: " REPO_URL

if [ -z "$REPO_URL" ]; then
    print_error "Repository URL is required"
    exit 1
fi

if [ -d ~/defi-project ]; then
    print_warning "Directory ~/defi-project exists, updating..."
    cd ~/defi-project
    git pull
else
    git clone "$REPO_URL" ~/defi-project
fi

cd ~/defi-project/backend
print_success "Repository cloned"

print_step "Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
print_success "Virtual environment created"

print_step "Installing Python dependencies..."
print_warning "This may take 10-15 minutes..."
pip install -r requirements.txt
print_success "Python dependencies installed"

print_step "Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh
print_success "Ollama installed"

print_step "Pulling TinyLlama model (1.1GB)..."
print_warning "This may take 10-15 minutes..."
ollama pull tinyllama
print_success "TinyLlama model downloaded"

print_step "Pulling embedding model..."
ollama pull all-minilm
print_success "Embedding model downloaded"

print_step "Configuring Ollama service..."
sudo tee /etc/systemd/system/ollama.service > /dev/null << EOF
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/local/bin/ollama serve
Environment="OLLAMA_HOST=127.0.0.1:11434"
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama

# Wait for Ollama to start
echo "Waiting for Ollama to start..."
sleep 5

# Verify Ollama is running
if curl -s http://localhost:11434 > /dev/null; then
    print_success "Ollama service started"
else
    print_error "Ollama service failed to start"
    exit 1
fi

print_step "Configuring backend environment..."
cat > .env << EOF
# Database
DATABASE_URL=postgresql+psycopg2://defi_user:${DB_PASSWORD}@localhost:5432/defi_risk_assessment

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
OLLAMA_TEMPERATURE=0.7
OLLAMA_EMBEDDING_MODEL=all-minilm

# RAG Configuration
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_TOP_K=5
VECTOR_STORE_PATH=/home/$USER/vectorstore

# MLflow
MLFLOW_TRACKING_URI=file:///home/$USER/mlruns

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=*
EOF

print_success "Environment configured"

print_step "Initializing database..."
source venv/bin/activate

# Run database initialization if scripts exist
if [ -f scripts/init_db.py ]; then
    python scripts/init_db.py
    print_success "Database initialized"
elif [ -f scripts/seed_real_protocols.py ]; then
    python scripts/seed_real_protocols.py
    print_success "Database seeded"
else
    print_warning "No database initialization scripts found"
    print_warning "You may need to initialize the database manually"
fi

print_step "Creating backend systemd service..."
sudo tee /etc/systemd/system/defi-backend.service > /dev/null << EOF
[Unit]
Description=DeFi Risk Assessment Backend
After=network.target postgresql.service ollama.service
Requires=postgresql.service ollama.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/defi-project/backend
Environment="PATH=/home/$USER/defi-project/backend/venv/bin"
ExecStart=/home/$USER/defi-project/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable defi-backend
sudo systemctl start defi-backend

echo "Waiting for backend to start..."
sleep 10

# Check if backend is running
if curl -s http://localhost:8000/api/v1/health > /dev/null; then
    print_success "Backend service started"
else
    print_warning "Backend may still be starting, check logs with: sudo journalctl -u defi-backend -f"
fi

print_step "Initializing vector store..."
print_warning "This may take 10-15 minutes..."

# Wait a bit more for backend to fully start
sleep 5

# Try to initialize vector store
if curl -X POST http://localhost:8000/api/v1/llm/initialize; then
    print_success "Vector store initialized"
else
    print_warning "Vector store initialization may have failed"
    print_warning "Try manually: curl -X POST http://localhost:8000/api/v1/llm/initialize"
fi

# Get external IP
EXTERNAL_IP=$(curl -s ifconfig.me)

echo ""
echo -e "${BLUE}=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

print_success "Services Status:"
echo "  Ollama: $(systemctl is-active ollama)"
echo "  Backend: $(systemctl is-active defi-backend)"
echo "  PostgreSQL: $(systemctl is-active postgresql)"
echo ""

print_success "Test Commands (on server):"
echo "  curl http://localhost:8000/api/v1/health"
echo "  curl http://localhost:8000/api/v1/llm/health"
echo ""

print_success "External Access:"
echo "  API URL: http://$EXTERNAL_IP:8000"
echo "  API Docs: http://$EXTERNAL_IP:8000/docs"
echo "  Health Check: http://$EXTERNAL_IP:8000/api/v1/health"
echo ""

print_warning "Important Notes:"
echo "  1. Database password saved in: ~/db_password.txt"
echo "  2. Test from your local machine:"
echo "     curl http://$EXTERNAL_IP:8000/api/v1/health"
echo ""

print_success "Management Commands:"
echo "  View logs: sudo journalctl -u defi-backend -f"
echo "  Restart backend: sudo systemctl restart defi-backend"
echo "  Refresh vector store: curl -X POST http://localhost:8000/api/v1/llm/refresh"
echo ""

print_success "Documentation:"
echo "  Full guide: TINYLLAMA_COMPLETE_SETUP.md"
echo "  Troubleshooting: Check logs with journalctl"
echo ""

echo -e "${GREEN}All done! Your TinyLlama-powered DeFi Risk Assessment system is ready!${NC}"
echo ""






