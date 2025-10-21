#!/bin/bash
# Complete GCP + TinyLlama Setup Script
# Run this on your GCP e2-medium instance
# Estimated time: 30-40 minutes

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================="
echo "DeFi Risk Assessment - GCP + TinyLlama"
echo -e "==========================================${NC}"
echo ""

# Check if running on Ubuntu
if [ ! -f /etc/lsb-release ]; then
    echo -e "${RED}Error: This script requires Ubuntu${NC}"
    exit 1
fi

echo -e "${GREEN}[1/12] Updating system...${NC}"
sudo apt update && sudo apt upgrade -y

echo -e "${GREEN}[2/12] Installing Python 3.11...${NC}"
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
sudo apt install -y git curl build-essential

echo -e "${GREEN}[3/12] Installing PostgreSQL...${NC}"
sudo apt install -y postgresql postgresql-contrib

echo -e "${GREEN}[4/12] Configuring PostgreSQL...${NC}"
DB_PASSWORD=$(openssl rand -base64 20)
echo "$DB_PASSWORD" > ~/db_password.txt
chmod 600 ~/db_password.txt

sudo -u postgres psql << EOF
CREATE USER defi_user WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE defi_risk_assessment OWNER defi_user;
GRANT ALL PRIVILEGES ON DATABASE defi_risk_assessment TO defi_user;
EOF

echo -e "${YELLOW}Database password saved to: ~/db_password.txt${NC}"

echo -e "${GREEN}[5/12] Cloning repository...${NC}"
read -p "Enter your GitHub repository URL: " REPO_URL

if [ -d ~/defi-project ]; then
    echo "Directory exists, updating..."
    cd ~/defi-project
    git pull
else
    git clone "$REPO_URL" ~/defi-project
fi

cd ~/defi-project/backend

echo -e "${GREEN}[6/12] Setting up Python environment...${NC}"
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}[7/12] Installing Ollama...${NC}"
curl -fsSL https://ollama.ai/install.sh | sh

echo -e "${GREEN}[8/12] Pulling TinyLlama model (1.1GB)...${NC}"
ollama pull tinyllama

echo -e "${GREEN}[9/12] Pulling embedding model (all-minilm)...${NC}"
ollama pull all-minilm
echo "Note: Using all-minilm instead of nomic-embed-text for GCP efficiency"

echo -e "${GREEN}[10/12] Configuring Ollama service...${NC}"
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

echo "Waiting for Ollama to start..."
sleep 5

echo -e "${GREEN}[11/12] Configuring backend environment...${NC}"
cat > .env << EOF
# Database
DATABASE_URL=postgresql+psycopg2://defi_user:${DB_PASSWORD}@localhost:5432/defi_risk_assessment

# Ollama (Local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
OLLAMA_TEMPERATURE=0.7
OLLAMA_TIMEOUT=120
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
EOF

echo -e "${GREEN}[12/12] Setting up backend service...${NC}"
sudo tee /etc/systemd/system/defi-backend.service > /dev/null << EOF
[Unit]
Description=DeFi Risk Assessment Backend
After=network.target postgresql.service ollama.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/defi-project/backend
Environment="PATH=/home/$USER/defi-project/backend/venv/bin"
ExecStart=/home/$USER/defi-project/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable defi-backend
sudo systemctl start defi-backend

echo "Waiting for backend to start..."
sleep 10

echo ""
echo -e "${BLUE}=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Get external IP
EXTERNAL_IP=$(curl -s ifconfig.me)

echo -e "${GREEN}✅ Services Status:${NC}"
echo "Ollama: $(systemctl is-active ollama)"
echo "Backend: $(systemctl is-active defi-backend)"
echo ""

echo -e "${GREEN}✅ Test Commands:${NC}"
echo "Health Check: curl http://localhost:8000/api/v1/health"
echo "LLM Health: curl http://localhost:8000/api/v1/llm/health"
echo ""

echo -e "${GREEN}✅ External Access:${NC}"
echo "API URL: http://$EXTERNAL_IP:8000"
echo "API Docs: http://$EXTERNAL_IP:8000/docs"
echo ""

echo -e "${YELLOW}⚠️ Important Next Steps:${NC}"
echo "1. Initialize vector store:"
echo "   curl -X POST http://localhost:8000/api/v1/llm/initialize"
echo ""
echo "2. Test from your local machine:"
echo "   curl http://$EXTERNAL_IP:8000/api/v1/health"
echo ""
echo "3. View logs:"
echo "   sudo journalctl -u defi-backend -f"
echo ""

echo -e "${YELLOW}Database password saved in: ~/db_password.txt${NC}"
echo ""

