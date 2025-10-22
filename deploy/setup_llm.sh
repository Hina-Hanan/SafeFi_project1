#!/bin/bash

set -e  # Exit on error

echo "======================================================"
echo "🤖 Ollama LLM Setup for DeFi Risk Assessment"
echo "======================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if running as postgres user
if [ "$(whoami)" != "postgres" ]; then
    print_error "This script must be run as postgres user"
    echo "Run: sudo su - postgres"
    exit 1
fi

# Step 1: Install Ollama
echo "Step 1: Installing Ollama..."
if command -v ollama &> /dev/null; then
    print_info "Ollama already installed: $(ollama --version)"
else
    print_info "Downloading and installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    print_success "Ollama installed"
fi
echo ""

# Step 2: Start Ollama service
echo "Step 2: Starting Ollama service..."
if pgrep -x "ollama" > /dev/null; then
    print_info "Ollama is already running"
else
    print_info "Starting Ollama in background..."
    nohup ollama serve > ~/ollama.log 2>&1 &
    sleep 5
    print_success "Ollama service started"
fi

# Verify Ollama is running
if curl -s http://localhost:11434/api/version > /dev/null; then
    VERSION=$(curl -s http://localhost:11434/api/version | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    print_success "Ollama is running (version: $VERSION)"
else
    print_error "Ollama failed to start"
    exit 1
fi
echo ""

# Step 3: Download model
echo "Step 3: Downloading TinyLlama model..."
if ollama list | grep -q "tinyllama"; then
    print_info "TinyLlama model already downloaded"
else
    print_info "Downloading TinyLlama (~637MB). This may take a few minutes..."
    ollama pull tinyllama
    print_success "TinyLlama model downloaded"
fi
echo ""

# Step 4: Test model
echo "Step 4: Testing model..."
print_info "Running quick test..."
TEST_RESPONSE=$(ollama run tinyllama "What is 2+2?" --verbose 2>&1 | head -5)
if [ -n "$TEST_RESPONSE" ]; then
    print_success "Model test successful"
else
    print_error "Model test failed"
fi
echo ""

# Step 5: Install Python dependencies
echo "Step 5: Installing LLM Python dependencies..."
cd /var/lib/postgresql/SafeFi_project1/backend
source venv/bin/activate

# Check disk space before installing
FREE_SPACE=$(df / | awk 'NR==2 {print $4}')
if [ $FREE_SPACE -lt 2000000 ]; then  # Less than 2GB
    print_error "Low disk space ($(($FREE_SPACE / 1024))MB free). Need at least 2GB for LLM dependencies."
    print_info "Skipping Python package installation"
    exit 1
fi

print_info "Installing langchain..."
pip install langchain==0.1.20 langchain-community==0.0.38 langchain-core==0.1.52 -q --no-cache-dir

print_info "Installing vector stores..."
pip install chromadb==0.4.24 faiss-cpu==1.8.0 -q --no-cache-dir

print_info "Installing document processors..."
pip install pypdf==4.2.0 python-docx==1.1.0 -q --no-cache-dir

print_success "Python dependencies installed"
echo ""

# Step 6: Update .env file
echo "Step 6: Updating .env file..."
if grep -q "OLLAMA_BASE_URL" .env; then
    print_info ".env already has Ollama configuration"
else
    cat >> .env << 'EOF'

# Ollama/LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
OLLAMA_TEMPERATURE=0.7
OLLAMA_EMBEDDING_MODEL=all-minilm
OLLAMA_TIMEOUT=120

# RAG Configuration
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_TOP_K=5
VECTOR_STORE_PATH=/var/lib/postgresql/vectorstore
EOF
    print_success ".env file updated"
fi
echo ""

# Step 7: Initialize vector store
echo "Step 7: Initializing vector store..."
export PYTHONPATH=/var/lib/postgresql/SafeFi_project1/backend:$PYTHONPATH

if [ -d "/var/lib/postgresql/vectorstore" ]; then
    print_info "Vector store already exists"
else
    print_info "Creating vector store..."
    if python3 scripts/initialize_vector_store.py 2>/dev/null; then
        print_success "Vector store initialized"
    else
        print_info "Vector store will be initialized on first backend startup"
    fi
fi
echo ""

# Step 8: Final verification
echo "Step 8: Final verification..."

# Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null; then
    print_success "Ollama API is accessible"
else
    print_error "Ollama API is not accessible"
fi

# Check model
if ollama list | grep -q "tinyllama"; then
    print_success "TinyLlama model is available"
else
    print_error "TinyLlama model is not available"
fi

# Check Python packages
if python3 -c "import langchain; import chromadb; import faiss" 2>/dev/null; then
    print_success "Python LLM packages are installed"
else
    print_error "Some Python LLM packages are missing"
fi

echo ""
echo "======================================================"
print_success "Ollama LLM Setup Complete!"
echo "======================================================"
echo ""
echo "To test:"
echo "  1. Start backend: uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "  2. Check health: curl http://localhost:8000/api/v1/llm/health"
echo "  3. Ask question: curl -X POST http://localhost:8000/api/v1/llm/ask -H 'Content-Type: application/json' -d '{\"question\": \"What is DeFi?\"}'"
echo ""
echo "To manage Ollama:"
echo "  Status: curl http://localhost:11434/api/version"
echo "  Models: ollama list"
echo "  Chat: ollama run tinyllama"
echo "  Logs: tail -f ~/ollama.log"
echo ""

# Show disk usage
print_info "Disk usage:"
df -h /





