#!/bin/bash
# GCP Backend Setup Script
# Run this on your GCP e2-micro instance

set -e

echo "=========================================="
echo "DeFi Risk Assessment - GCP Setup"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Ubuntu
if [ ! -f /etc/lsb-release ]; then
    echo -e "${RED}Error: This script is designed for Ubuntu${NC}"
    exit 1
fi

echo -e "${GREEN}[1/10] Updating system...${NC}"
sudo apt update && sudo apt upgrade -y

echo -e "${GREEN}[2/10] Installing Python 3.11...${NC}"
sudo apt install -y python3.11 python3.11-venv python3-pip git curl

echo -e "${GREEN}[3/10] Installing PostgreSQL...${NC}"
sudo apt install -y postgresql postgresql-contrib

echo -e "${GREEN}[4/10] Configuring PostgreSQL...${NC}"
# Generate random password
DB_PASSWORD=$(openssl rand -base64 32)
sudo -u postgres psql -c "CREATE USER defi_user WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "CREATE DATABASE defi_risk_assessment OWNER defi_user;" 2>/dev/null || echo "Database already exists"

echo -e "${GREEN}[5/10] Cloning repository...${NC}"
read -p "Enter your GitHub repository URL: " REPO_URL
if [ ! -d ~/defi-risk-assessment ]; then
    git clone $REPO_URL ~/defi-risk-assessment
else
    echo "Repository already cloned"
fi

cd ~/defi-risk-assessment/backend

echo -e "${GREEN}[6/10] Creating Python virtual environment...${NC}"
python3.11 -m venv venv
source venv/bin/activate

echo -e "${GREEN}[7/10] Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}[8/10] Configuring environment variables...${NC}"
echo ""
echo -e "${YELLOW}Important: You need to provide your local Ollama URL${NC}"
echo ""
echo "Choose your connection method:"
echo "1) ngrok (e.g., https://abc123.ngrok.io)"
echo "2) Tailscale (e.g., http://100.x.x.x:11434)"
echo "3) Direct IP (e.g., http://YOUR_IP:11434)"
read -p "Enter choice (1-3): " CONNECTION_CHOICE

read -p "Enter your Ollama URL: " OLLAMA_URL

# Create .env file
cat > .env << EOF
# Database
DATABASE_URL=postgresql+psycopg2://defi_user:$DB_PASSWORD@localhost:5432/defi_risk_assessment

# Ollama Configuration
OLLAMA_BASE_URL=$OLLAMA_URL
OLLAMA_MODEL=mistral
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
EOF

echo -e "${GREEN}.env file created${NC}"
echo "Database password: $DB_PASSWORD"
echo -e "${YELLOW}IMPORTANT: Save this password securely!${NC}"

echo -e "${GREEN}[9/10] Initializing database...${NC}"
# Run migrations if they exist
if [ -f alembic.ini ]; then
    python -m alembic upgrade head
fi

# Seed data
if [ -f scripts/seed_real_protocols.py ]; then
    python scripts/seed_real_protocols.py
fi

echo -e "${GREEN}[10/10] Setting up systemd service...${NC}"
sudo tee /etc/systemd/system/defi-backend.service > /dev/null << EOF
[Unit]
Description=DeFi Risk Assessment Backend
After=network.target postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/defi-risk-assessment/backend
Environment="PATH=/home/$USER/defi-risk-assessment/backend/venv/bin"
ExecStart=/home/$USER/defi-risk-assessment/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable defi-backend
sudo systemctl start defi-backend

echo ""
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Service Status:"
sudo systemctl status defi-backend --no-pager
echo ""
echo "Next Steps:"
echo "1. Test backend: curl http://localhost:8000/api/v1/health"
echo "2. Initialize vector store: curl -X POST http://localhost:8000/api/v1/llm/initialize"
echo "3. Configure firewall to allow port 8000"
echo "4. Access from outside: curl http://YOUR_GCP_IP:8000/api/v1/health"
echo ""
echo "Logs: sudo journalctl -u defi-backend -f"
echo "Restart: sudo systemctl restart defi-backend"
echo ""


