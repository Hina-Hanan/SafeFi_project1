# 🚀 RAG LLM Assistant - Quick Start (10 Minutes)

## Prerequisites

- Python 3.8+ ✅
- 8GB+ RAM
- 5-10GB free disk space

---

## Step 1: Install Ollama (2 min)

### Windows
```powershell
winget install Ollama.Ollama
```

### macOS
```bash
brew install ollama
```

### Linux
```bash
curl https://ollama.ai/install.sh | sh
```

---

## Step 2: Pull Models (3 min)

```bash
# LLM Model (choose one)
ollama pull mistral         # Recommended for GCP hybrid (4.1GB, faster)
# OR
ollama pull llama3          # Alternative (4.7GB, excellent quality)

# Embedding Model (for RAG)
ollama pull nomic-embed-text
```

**Note:** If deploying to GCP free tier, use the **hybrid architecture** (see `HYBRID_DEPLOYMENT_GCP.md`):
- Backend on GCP (free tier)
- Ollama runs locally on your machine

---

## Step 3: Install Python Dependencies (2 min)

```bash
cd backend
pip install langchain==0.1.20 langchain-community==0.0.38 sentence-transformers==2.7.0 chromadb==0.4.24 faiss-cpu==1.8.0
```

---

## Step 4: Configure Environment (1 min)

Create `backend/.env`:

```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
OLLAMA_TEMPERATURE=0.7
RAG_TOP_K=5
```

---

## Step 5: Start Services (2 min)

**Terminal 1:**
```bash
ollama serve
```

**Terminal 2:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

---

## Step 6: Initialize & Test

```bash
# Initialize vector store
curl -X POST http://localhost:8000/api/v1/llm/initialize

# Test query
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What protocols are monitored?"}'
```

---

## ✅ Success!

If you see a response, your RAG LLM assistant is working!

---

## Example Queries

```bash
# Get high-risk protocols
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the high-risk protocols?"}'

# Check system status
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How many protocols are tracked?"}'

# Get protocol details
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about Uniswap"}'
```

---

## Troubleshooting

### "Ollama not available"
```bash
# Check if running
curl http://localhost:11434

# If not, start it
ollama serve
```

### "Vector store not initialized"
```bash
curl -X POST http://localhost:8000/api/v1/llm/initialize
```

### "Model not found"
```bash
ollama list
ollama pull llama3
```

---

## Next Steps

📖 **Full Documentation**: See `RAG_LLM_INTEGRATION.md`  
🔧 **API Reference**: Check the full guide for all endpoints  
💡 **Advanced Usage**: Learn about streaming, custom prompts, etc.

---

**Total Setup Time: ~10 minutes**  
**Cost: $0 forever** 💰  
**Privacy: 100% local** 🔒  

Enjoy your free RAG-powered LLM assistant! 🎉

