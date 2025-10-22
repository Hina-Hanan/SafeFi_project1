#!/bin/bash
# TinyLlama Local Setup Script for Mac/Linux
# This script automates TinyLlama setup on your local machine

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "TinyLlama Local Setup (Mac/Linux)"
echo "==========================================${NC}"
echo ""

# Check if Ollama is installed
echo -e "${BLUE}[1/6] Checking Ollama installation...${NC}"
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}ERROR: Ollama not found!${NC}"
    echo ""
    echo "Please install Ollama first:"
    echo "  Mac: brew install ollama"
    echo "  Linux: curl -fsSL https://ollama.ai/install.sh | sh"
    echo ""
    exit 1
fi
echo -e "${GREEN}✓ Ollama is installed${NC}"
echo ""

# Check if Ollama service is running
echo -e "${BLUE}[2/6] Checking Ollama service...${NC}"
if ! curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo -e "${YELLOW}WARNING: Ollama service not responding${NC}"
    echo "Starting Ollama..."
    
    # Try to start Ollama in background
    nohup ollama serve > /dev/null 2>&1 &
    sleep 5
    
    if ! curl -s http://localhost:11434 > /dev/null 2>&1; then
        echo -e "${RED}ERROR: Ollama service failed to start${NC}"
        echo "Please start Ollama manually:"
        echo "  ollama serve"
        echo ""
        echo "Then run this script again."
        exit 1
    fi
fi
echo -e "${GREEN}✓ Ollama service is running${NC}"
echo ""

# Pull TinyLlama model
echo -e "${BLUE}[3/6] Pulling TinyLlama model (1.1GB)...${NC}"
echo -e "${YELLOW}This may take 5-10 minutes depending on your connection...${NC}"
ollama pull tinyllama
echo -e "${GREEN}✓ TinyLlama model downloaded${NC}"
echo ""

# Pull embedding model
echo -e "${BLUE}[4/6] Pulling all-minilm embedding model (91MB)...${NC}"
ollama pull all-minilm
echo -e "${GREEN}✓ Embedding model downloaded${NC}"
echo ""

# Verify models
echo -e "${BLUE}[5/6] Verifying models...${NC}"
ollama list
echo ""

# Check/Update .env file
echo -e "${BLUE}[6/6] Checking environment configuration...${NC}"
if [ ! -f .env ]; then
    echo -e "${YELLOW}WARNING: .env file not found${NC}"
    echo "Creating .env with Ollama settings..."
    
    cat > .env << 'EOF'
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
OLLAMA_TEMPERATURE=0.7
OLLAMA_EMBEDDING_MODEL=all-minilm

# RAG Configuration
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_TOP_K=5
VECTOR_STORE_PATH=./data/vectorstore
EOF
    
    echo -e "${GREEN}✓ .env file created${NC}"
    echo ""
    echo -e "${YELLOW}IMPORTANT: Add your DATABASE_URL to .env file!${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
    echo ""
    echo "Please verify these settings in your .env file:"
    echo "  OLLAMA_BASE_URL=http://localhost:11434"
    echo "  OLLAMA_MODEL=tinyllama"
    echo "  OLLAMA_EMBEDDING_MODEL=all-minilm"
fi
echo ""

echo -e "${BLUE}=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo -e "${GREEN}✓ Ollama installed and running${NC}"
echo -e "${GREEN}✓ TinyLlama model ready${NC}"
echo -e "${GREEN}✓ Embedding model ready${NC}"
echo -e "${GREEN}✓ Environment configured${NC}"
echo ""
echo "Next Steps:"
echo "  1. Verify DATABASE_URL in .env file"
echo "  2. Start backend:"
echo "     source venv/bin/activate"
echo "     python -m uvicorn app.main:app --reload"
echo "  3. Initialize vector store:"
echo "     curl -X POST http://localhost:8000/api/v1/llm/initialize"
echo "  4. Test:"
echo "     curl http://localhost:8000/api/v1/llm/health"
echo ""
echo "Full documentation: TINYLLAMA_COMPLETE_SETUP.md"
echo ""






