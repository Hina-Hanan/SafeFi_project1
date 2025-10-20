# RAG LLM API Examples

Complete API usage examples for the RAG-powered LLM assistant.

---

## Base URL

```
http://localhost:8000/api/v1/llm
```

---

## 1. Health Check

**Check if the LLM assistant is ready**

### cURL
```bash
curl -X GET http://localhost:8000/api/v1/llm/health
```

### Python
```python
import requests
response = requests.get("http://localhost:8000/api/v1/llm/health")
print(response.json())
```

### Response
```json
{
  "ollama_available": true,
  "vector_store_initialized": true,
  "model": "llama3",
  "message": "LLM Assistant is ready"
}
```

---

## 2. Initialize Vector Store

**Create vector embeddings from database documents**

### cURL
```bash
curl -X POST http://localhost:8000/api/v1/llm/initialize
```

### Python
```python
response = requests.post("http://localhost:8000/api/v1/llm/initialize")
print(response.json())
```

### Response
```json
{
  "initialized": true,
  "document_count": 45,
  "message": "Vector store initialized successfully"
}
```

---

## 3. Query (Non-Streaming)

**Ask questions and get complete responses**

### Example 1: High-Risk Protocols

```bash
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the current high-risk protocols?",
    "top_k": 5,
    "temperature": 0.7
  }'
```

### Example 2: Protocol Details

```bash
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about Uniswap"}'
```

### Example 3: System Statistics

```bash
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How many protocols are being tracked?"}'
```

### Python
```python
query_data = {
    "query": "What are the high-risk protocols?",
    "top_k": 5,
    "temperature": 0.7
}
response = requests.post(
    "http://localhost:8000/api/v1/llm/query",
    json=query_data
)
print(response.json()["answer"])
```

---

## 4. Query (Streaming)

**Get real-time streaming responses**

### cURL
```bash
curl -X POST http://localhost:8000/api/v1/llm/query/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain DeFi risk factors"}'
```

### Python (Streaming)
```python
import httpx

async def stream_query(question: str):
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            "http://localhost:8000/api/v1/llm/query/stream",
            json={"query": question},
            timeout=120.0
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    token = line[6:]
                    if token == "[DONE]":
                        break
                    print(token, end="", flush=True)

# Usage
import asyncio
asyncio.run(stream_query("What is TVL?"))
```

---

## 5. Get Context Documents

**Retrieve context without generating response (for debugging)**

### cURL
```bash
curl -X GET "http://localhost:8000/api/v1/llm/context/Uniswap?top_k=3"
```

### Python
```python
response = requests.get(
    "http://localhost:8000/api/v1/llm/context/Uniswap",
    params={"top_k": 3}
)
documents = response.json()["documents"]
for doc in documents:
    print(doc["content"][:200])
```

---

## 6. Refresh Vector Store

**Update vector store with latest database data**

### cURL
```bash
curl -X POST http://localhost:8000/api/v1/llm/refresh
```

### Python
```python
response = requests.post("http://localhost:8000/api/v1/llm/refresh")
print(response.json())
```

---

## Complete Python Client

```python
import requests
import asyncio
import httpx
from typing import Dict, List, Optional


class RAGLLMClient:
    """Client for RAG LLM Assistant API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1/llm"
    
    def health(self) -> Dict:
        """Check health status."""
        response = requests.get(f"{self.api_base}/health")
        response.raise_for_status()
        return response.json()
    
    def initialize(self) -> Dict:
        """Initialize vector store."""
        response = requests.post(f"{self.api_base}/initialize")
        response.raise_for_status()
        return response.json()
    
    def refresh(self) -> Dict:
        """Refresh vector store with latest data."""
        response = requests.post(f"{self.api_base}/refresh")
        response.raise_for_status()
        return response.json()
    
    def query(
        self,
        question: str,
        top_k: int = 5,
        temperature: float = 0.7
    ) -> str:
        """Query LLM and get answer."""
        response = requests.post(
            f"{self.api_base}/query",
            json={
                "query": question,
                "top_k": top_k,
                "temperature": temperature
            },
            timeout=60.0
        )
        response.raise_for_status()
        return response.json()["answer"]
    
    async def query_stream(self, question: str, top_k: int = 5):
        """Stream LLM response."""
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.api_base}/query/stream",
                json={"query": question, "top_k": top_k},
                timeout=120.0
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        token = line[6:]
                        if token == "[DONE]":
                            break
                        yield token
    
    def get_context(self, query: str, top_k: int = 5) -> List[Dict]:
        """Get relevant context documents."""
        response = requests.get(
            f"{self.api_base}/context/{query}",
            params={"top_k": top_k}
        )
        response.raise_for_status()
        return response.json()["documents"]


# Usage Examples
if __name__ == "__main__":
    client = RAGLLMClient()
    
    # Check health
    health = client.health()
    print(f"Status: {health['message']}")
    
    # Initialize if needed
    if not health['vector_store_initialized']:
        result = client.initialize()
        print(f"Initialized: {result['message']}")
    
    # Ask questions
    print("\n--- Query 1 ---")
    answer = client.query("What are the high-risk protocols?")
    print(answer)
    
    print("\n--- Query 2 ---")
    answer = client.query("Which protocol has the highest TVL?")
    print(answer)
    
    # Get context
    print("\n--- Context for 'Uniswap' ---")
    context = client.get_context("Uniswap", top_k=2)
    for i, doc in enumerate(context, 1):
        print(f"\nDocument {i}:")
        print(doc["content"][:300])
    
    # Streaming example
    print("\n--- Streaming Query ---")
    async def demo_stream():
        async for token in client.query_stream("What is DeFi?"):
            print(token, end="", flush=True)
        print()
    
    asyncio.run(demo_stream())
```

---

## JavaScript/TypeScript Example

```typescript
interface QueryRequest {
  query: string;
  top_k?: number;
  temperature?: number;
}

interface QueryResponse {
  answer: string;
  context_used: number;
  model: string;
}

interface HealthResponse {
  ollama_available: boolean;
  vector_store_initialized: boolean;
  model: string;
  message: string;
}

class RAGLLMClient {
  private baseUrl: string;
  private apiBase: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.apiBase = `${baseUrl}/api/v1/llm`;
  }

  async health(): Promise<HealthResponse> {
    const response = await fetch(`${this.apiBase}/health`);
    return response.json();
  }

  async initialize() {
    const response = await fetch(`${this.apiBase}/initialize`, {
      method: 'POST'
    });
    return response.json();
  }

  async query(request: QueryRequest): Promise<QueryResponse> {
    const response = await fetch(`${this.apiBase}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    return response.json();
  }

  async *queryStream(request: QueryRequest): AsyncGenerator<string> {
    const response = await fetch(`${this.apiBase}/query/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) return;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value);
      const lines = text.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const token = line.slice(6);
          if (token === '[DONE]') return;
          yield token;
        }
      }
    }
  }
}

// Usage
const client = new RAGLLMClient();

// Check health
const health = await client.health();
console.log(health.message);

// Query
const response = await client.query({
  query: 'What are the high-risk protocols?',
  top_k: 5
});
console.log(response.answer);

// Stream
for await (const token of client.queryStream({
  query: 'Explain DeFi'
})) {
  process.stdout.write(token);
}
```

---

## Common Query Patterns

### Protocol Information

```bash
# List all protocols
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What protocols are monitored?"}'

# Specific protocol details
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about Aave"}'

# Protocol comparison
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare Uniswap and SushiSwap"}'
```

### Risk Analysis

```bash
# High-risk protocols
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the high-risk protocols?"}'

# Risk explanation
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Why is Protocol X high risk?"}'

# Risk methodology
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How are risk scores calculated?"}'
```

### Metrics & Statistics

```bash
# TVL queries
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Which protocol has the highest TVL?"}'

# Volume queries
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me 24h trading volumes"}'

# System statistics
curl -X POST http://localhost:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the system statistics?"}'
```

---

## Response Examples

### Protocol Query

**Query:** "Tell me about Uniswap"

**Response:**
```json
{
  "answer": "Uniswap is a decentralized exchange (DEX) protocol on Ethereum. Based on current data:\n\n- Category: DEX\n- Total Value Locked (TVL): $5.2 billion\n- 24h Volume: $1.8 billion\n- Risk Level: LOW\n- Risk Score: 0.25\n- Volatility Score: 0.18 (stable)\n- Liquidity Score: 0.95 (excellent)\n\nUniswap is considered one of the safest and most liquid DeFi protocols.",
  "context_used": 3,
  "model": "llama3"
}
```

### High-Risk Query

**Query:** "What are the high-risk protocols?"

**Response:**
```json
{
  "answer": "Based on current risk assessments, the following protocols are classified as HIGH RISK:\n\n1. **Protocol X** (Risk Score: 0.85)\n   - Volatility: 0.92 (very high)\n   - Liquidity: 0.45 (low)\n   - Recent 24h price change: -15.3%\n\n2. **Protocol Y** (Risk Score: 0.78)\n   - TVL dropped 25% in last 7 days\n   - Increased trading volume volatility\n   - Liquidity concerns\n\nThese protocols show elevated risk factors and should be monitored closely.",
  "context_used": 5,
  "model": "llama3"
}
```

---

## Error Handling

### Check for Errors

```python
try:
    response = requests.post(
        "http://localhost:8000/api/v1/llm/query",
        json={"query": "test"},
        timeout=60.0
    )
    response.raise_for_status()
    result = response.json()
    print(result["answer"])
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.ConnectionError:
    print("Cannot connect to server")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e.response.status_code}")
    print(e.response.json())
```

### Common Errors

**503 Service Unavailable**
- Ollama is not running
- Solution: `ollama serve`

**500 Internal Server Error**
- Vector store not initialized
- Solution: Call `/initialize` endpoint

**400 Bad Request**
- Invalid query parameters
- Solution: Check request format

---

## Performance Tips

1. **Use smaller `top_k` for faster responses:**
   ```json
   {"query": "...", "top_k": 3}
   ```

2. **Lower temperature for more focused answers:**
   ```json
   {"query": "...", "temperature": 0.5}
   ```

3. **Cache common queries in your application**

4. **Use streaming for better UX with long responses**

5. **Refresh vector store periodically (not on every query):**
   ```bash
   # Run hourly via cron
   curl -X POST http://localhost:8000/api/v1/llm/refresh
   ```

---

## Testing Script

```bash
#!/bin/bash
# test_rag_api.sh

BASE_URL="http://localhost:8000/api/v1/llm"

echo "Testing RAG LLM API..."

# Health check
echo -e "\n1. Health Check:"
curl -s "$BASE_URL/health" | jq

# Initialize
echo -e "\n2. Initialize Vector Store:"
curl -s -X POST "$BASE_URL/initialize" | jq

# Query
echo -e "\n3. Query Test:"
curl -s -X POST "$BASE_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What protocols are monitored?", "top_k": 3}' | jq

# Context
echo -e "\n4. Context Retrieval:"
curl -s "$BASE_URL/context/Uniswap?top_k=2" | jq

echo -e "\nAll tests complete!"
```

---

**You now have everything you need to integrate the RAG LLM assistant!** 🚀


