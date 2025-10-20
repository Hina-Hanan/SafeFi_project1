# RAG-Powered LLM Assistant Integration Guide

## 🎯 Overview

This guide shows how to integrate a **free, open-source LLM** with **Retrieval-Augmented Generation (RAG)** to answer questions about your DeFi protocols, risk scores, and metrics using **real database context**.

### What is RAG?

**RAG (Retrieval-Augmented Generation)** combines:
1. **Vector Search**: Find relevant information from your database
2. **LLM Generation**: Generate accurate answers using that context
3. **Result**: Fact-based responses grounded in your actual data

### Technology Stack

- **LLM**: Ollama (Llama 3, Mistral, DeepSeek, Phi-3)
- **RAG Framework**: LangChain
- **Vector Store**: FAISS (in-memory) or ChromaDB (persistent)
- **Embeddings**: HuggingFace sentence-transformers
- **API**: FastAPI with streaming support

---

## 🚀 Quick Start (10 Minutes)

### Step 1: Install Dependencies

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# This includes:
# - langchain & langchain-community
# - sentence-transformers
# - chromadb & faiss-cpu
# - httpx
```

### Step 2: Install & Setup Ollama

#### Install Ollama

**Windows:**
```powershell
winget install Ollama.Ollama
```

**macOS/Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

#### Pull an LLM Model

```bash
# Recommended: Llama 3 (4.7GB)
ollama pull llama3

# OR DeepSeek (lightweight, 4GB)
ollama pull deepseek-coder

# OR Mistral (fast, 4.1GB)
ollama pull mistral

# OR Phi-3 (Microsoft, 2.3GB)
ollama pull phi3
```

#### Pull Embedding Model

```bash
# For RAG vector embeddings
ollama pull nomic-embed-text
```

### Step 3: Configure Environment

Create or update `backend/.env`:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
OLLAMA_TEMPERATURE=0.7
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# RAG Configuration
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_TOP_K=5
VECTOR_STORE_PATH=./data/vectorstore
```

### Step 4: Start Services

**Terminal 1 - Ollama:**
```bash
ollama serve
```

**Terminal 2 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Step 5: Initialize Vector Store

```bash
# Initialize vector store with database documents
curl -X POST http://localhost:8000/api/v1/llm/initialize
```

**Response:**
```json
{
  "initialized": true,
  "document_count": 45,
  "message": "Vector store initialized successfully"
}
```

### Step 6: Query the Assistant!

```bash
# Ask a question
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the current high-risk protocols?"}'
```

**Response:**
```json
{
  "answer": "Based on the current risk assessments, the high-risk protocols are:\n\n1. Protocol X (DeFi) - Risk Score: 0.85\n2. Protocol Y (DEX) - Risk Score: 0.78\n...",
  "context_used": 5,
  "model": "llama3"
}
```

---

## 📚 API Reference

### Base URL

```
http://localhost:8000/api/v1/llm
```

### Endpoints

#### 1. Health Check

**GET** `/health`

Check if LLM and vector store are ready.

```bash
curl http://localhost:8000/api/v1/llm/health
```

**Response:**
```json
{
  "ollama_available": true,
  "vector_store_initialized": true,
  "model": "llama3",
  "message": "LLM Assistant is ready"
}
```

---

#### 2. Initialize Vector Store

**POST** `/initialize`

Load database documents and create vector embeddings.

```bash
curl -X POST http://localhost:8000/api/v1/llm/initialize
```

**When to call:**
- First time setup
- After database schema changes
- When starting fresh

---

#### 3. Refresh Vector Store

**POST** `/refresh`

Update vector store with latest database data.

```bash
curl -X POST http://localhost:8000/api/v1/llm/refresh
```

**When to call:**
- After adding new protocols
- After risk score updates
- Periodically (e.g., every hour)

---

#### 4. Query (Non-Streaming)

**POST** `/query`

Ask a question and get a complete response.

```bash
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which protocol has the highest TVL?",
    "top_k": 5,
    "temperature": 0.7
  }'
```

**Request Body:**
```typescript
{
  query: string,        // Your question (required)
  top_k?: number,       // Number of context docs (default: 5)
  temperature?: number  // Response creativity 0.0-1.0 (default: 0.7)
}
```

**Response:**
```json
{
  "answer": "According to the latest metrics, Uniswap has the highest TVL at $5.2 billion...",
  "context_used": 5,
  "model": "llama3"
}
```

---

#### 5. Query (Streaming)

**POST** `/query/stream`

Get real-time streaming response (Server-Sent Events).

```bash
curl -X POST http://localhost:8000/api/v1/llm/query/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain DeFi risk factors"}'
```

**Response (SSE):**
```
data: DeFi
data:  risk
data:  factors
data:  include
data: ...
data: [DONE]
```

**Python Example:**
```python
import httpx

async with httpx.AsyncClient() as client:
    async with client.stream(
        "POST",
        "http://localhost:8000/api/v1/llm/query/stream",
        json={"query": "What is TVL?"},
    ) as response:
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                token = line[6:]
                if token == "[DONE]":
                    break
                print(token, end="", flush=True)
```

---

#### 6. Get Context

**GET** `/context/{query}`

Retrieve relevant context documents without generating response (useful for debugging).

```bash
curl "http://localhost:8000/api/v1/llm/context/Uniswap?top_k=3"
```

**Response:**
```json
{
  "query": "Uniswap",
  "documents_found": 3,
  "documents": [
    {
      "content": "Protocol: Uniswap\nSymbol: UNI\nCategory: dex\n...",
      "metadata": {
        "source": "database",
        "type": "protocol",
        "protocol_name": "Uniswap",
        "risk_level": "low"
      }
    }
  ]
}
```

---

## 🔧 Architecture

### System Flow

```
User Query
    ↓
FastAPI Endpoint (/api/v1/llm/query)
    ↓
RAG LLM Service
    ├─→ Vector Store (semantic search)
    │       ├─→ FAISS/ChromaDB
    │       └─→ HuggingFace Embeddings
    │
    ├─→ Document Retrieval (top K results)
    │
    ├─→ Context Building (format documents)
    │
    └─→ LLM Generation (Ollama)
            ├─→ Llama 3 / Mistral / DeepSeek
            └─→ Response with Context
```

### Components

#### 1. **Document Loaders** (`document_loaders.py`)
- Converts database records to text documents
- Loads protocols, metrics, risk scores
- Creates structured content with metadata

#### 2. **Vector Store** (`vector_store.py`)
- Embeds documents using sentence-transformers
- Stores in FAISS (fast in-memory) or ChromaDB (persistent)
- Performs semantic similarity search

#### 3. **LLM Service** (`llm_service.py`)
- Integrates LangChain with Ollama
- Manages RAG pipeline
- Handles streaming and non-streaming responses

#### 4. **API Endpoints** (`llm_assistant.py`)
- FastAPI routes for HTTP access
- Request validation with Pydantic
- Error handling and logging

---

## 💡 Example Queries

### Protocol Information

**Query:** "What protocols are being monitored?"

**Response:**
```
We are currently monitoring 42 DeFi protocols across multiple categories:
- DEXs: Uniswap, SushiSwap, PancakeSwap
- Lending: Aave, Compound, MakerDAO
- Derivatives: dYdX, GMX
- Yield: Yearn Finance, Curve
...
```

---

### Risk Analysis

**Query:** "What are the high-risk protocols and why?"

**Response:**
```
Based on current risk assessments, the high-risk protocols are:

1. Protocol X (Risk Score: 0.85)
   - High volatility score: 0.92
   - Low liquidity score: 0.45
   - 24h price change: -15.3%

2. Protocol Y (Risk Score: 0.78)
   - Recent TVL drop: 25%
   - Increased trading volume volatility
...
```

---

### Metrics & Trends

**Query:** "Which protocol has the highest TVL and what is its risk level?"

**Response:**
```
Uniswap has the highest Total Value Locked (TVL) at $5.2 billion.

Risk Assessment:
- Risk Level: LOW
- Risk Score: 0.25
- Volatility: 0.18 (stable)
- Liquidity: 0.95 (excellent)

This makes Uniswap one of the safest protocols in our monitoring system.
```

---

## 🎓 Understanding RAG

### How It Works

1. **Document Loading**
   ```python
   # Load protocols from database
   protocols = db.query(Protocol).all()
   
   # Convert to text documents
   documents = [
       Document(
           page_content=f"Protocol: {p.name}\nTVL: ${p.tvl}...",
           metadata={"protocol_id": p.id}
       )
       for p in protocols
   ]
   ```

2. **Embedding Creation**
   ```python
   # Create vector embeddings
   embeddings = HuggingFaceEmbeddings(
       model_name="sentence-transformers/all-MiniLM-L6-v2"
   )
   
   # Store in vector database
   vectorstore = FAISS.from_documents(documents, embeddings)
   ```

3. **Semantic Search**
   ```python
   # Find relevant documents
   query = "high risk protocols"
   relevant_docs = vectorstore.similarity_search(query, k=5)
   ```

4. **Context-Aware Generation**
   ```python
   # Build prompt with context
   prompt = f"""
   Context: {relevant_docs}
   Question: {query}
   Answer:
   """
   
   # Generate response
   response = ollama.generate(prompt)
   ```

### Why RAG?

**Without RAG:**
- LLM only knows its training data
- No access to your specific protocols
- May hallucinate incorrect information

**With RAG:**
- ✅ Grounded in your actual database
- ✅ Always up-to-date information
- ✅ Fact-based, verifiable responses
- ✅ Can cite sources and metrics

---

## ⚙️ Configuration

### Model Selection

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **llama3** | 4.7GB | Medium | Excellent | Recommended |
| deepseek-coder | 4GB | Fast | Very Good | Code-focused |
| mistral | 4.1GB | Fast | Excellent | Speed priority |
| phi3 | 2.3GB | Very Fast | Good | Low-end systems |

### RAG Parameters

**RAG_CHUNK_SIZE** (default: 500)
- Text chunk size for embeddings
- Larger = more context, slower
- Smaller = faster, less context

**RAG_CHUNK_OVERLAP** (default: 50)
- Overlap between chunks
- Prevents context loss at boundaries

**RAG_TOP_K** (default: 5)
- Number of documents to retrieve
- More = better context, slower
- Less = faster, may miss info

**Temperature** (default: 0.7)
- 0.0-0.3: Focused, factual
- 0.4-0.7: Balanced
- 0.8-1.0: Creative, varied

---

## 🐛 Troubleshooting

### "Ollama service not available"

**Solution:**
```bash
# Start Ollama
ollama serve

# Verify it's running
curl http://localhost:11434
```

---

### "Vector store not initialized"

**Solution:**
```bash
# Initialize vector store
curl -X POST http://localhost:8000/api/v1/llm/initialize
```

---

### "Model not found"

**Solution:**
```bash
# List installed models
ollama list

# Pull the model
ollama pull llama3
```

---

### "Empty or irrelevant responses"

**Possible Causes:**
1. Vector store not refreshed after database updates
2. Query too vague
3. No matching context in database

**Solutions:**
```bash
# Refresh vector store
curl -X POST http://localhost:8000/api/v1/llm/refresh

# Be more specific in queries
# ❌ "Tell me about protocols"
# ✅ "What is Uniswap's current risk score?"

# Check what context is retrieved
curl "http://localhost:8000/api/v1/llm/context/your-query"
```

---

### "Slow responses"

**Solutions:**
1. Use smaller model: `ollama pull phi3`
2. Reduce `top_k` in queries: `"top_k": 3`
3. Use FAISS instead of ChromaDB (faster, in-memory)
4. Lower temperature: `"temperature": 0.5`

---

## 🔒 Security Considerations

### Local-Only Deployment

- Ollama runs on `localhost:11434` (not exposed to network)
- All data processing happens locally
- No data sent to external services
- Complete privacy

### Production Deployment

If exposing to network:
```python
# Add authentication
from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403)
    return api_key

# Protect endpoints
@router.post("/query", dependencies=[Depends(verify_api_key)])
async def query_llm(...):
    ...
```

---

## 📊 Performance Optimization

### Vector Store

**FAISS (In-Memory):**
- ✅ Very fast search
- ✅ Lower latency
- ❌ Not persistent
- ❌ Higher RAM usage

**ChromaDB (Persistent):**
- ✅ Persistent storage
- ✅ Lower RAM usage
- ❌ Slightly slower
- ✅ Survives restarts

### Embedding Models

| Model | Dimensions | Speed | Quality |
|-------|------------|-------|---------|
| all-MiniLM-L6-v2 | 384 | Fast | Good |
| all-mpnet-base-v2 | 768 | Medium | Excellent |
| nomic-embed-text | 768 | Medium | Excellent |

### Caching

Implement response caching for common queries:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(query: str, top_k: int) -> str:
    return llm_service.generate_response(query)
```

---

## 🎯 Advanced Features

### Custom Prompts

Modify the system prompt in `llm_service.py`:

```python
RAG_PROMPT_TEMPLATE = """
You are a DeFi expert assistant.

Context: {context}
Question: {question}

Provide a detailed, technical answer with specific metrics.
"""
```

### Metadata Filtering

Filter context by protocol category:

```python
# Only retrieve DEX protocols
context_docs = vectorstore.similarity_search(
    query,
    k=5,
    filter={"category": "dex"}
)
```

### Conversation Memory

Add conversation history (not yet implemented):

```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory()
# Store and retrieve conversation context
```

---

## 📈 Cost Analysis

### Local (Ollama + RAG)

**One-Time:**
- Setup time: ~10 minutes
- Model download: ~5GB disk space

**Ongoing:**
- Compute: $0/month (local hardware)
- API calls: $0/month (unlimited)
- Privacy: 100% (all local)

**Total Annual Cost: $0** 💚

### Cloud Alternatives

**OpenAI GPT-4:**
- Input: $10/million tokens
- Output: $30/million tokens
- Typical cost: $100-500/month

**Anthropic Claude:**
- Input: $3/million tokens
- Output: $15/million tokens
- Typical cost: $50-300/month

**Annual Savings: $600-6000!** 🎉

---

## 🚀 Next Steps

1. ✅ Complete setup following Quick Start
2. ✅ Test with example queries
3. ✅ Integrate into your application
4. ✅ Monitor performance and optimize
5. ✅ Add custom prompts for your use case
6. 🔄 Implement caching and optimization
7. 🔄 Add authentication for production
8. 🔄 Set up automated vector store refresh

---

## 📚 Additional Resources

- **Ollama Docs**: https://ollama.ai/docs
- **LangChain Docs**: https://python.langchain.com/docs
- **FAISS**: https://faiss.ai
- **Sentence Transformers**: https://www.sbert.net

---

**Congratulations! You now have a production-ready RAG-powered LLM assistant!** 🎉

Questions? Check the troubleshooting section or review the code in `backend/app/services/rag/`.


