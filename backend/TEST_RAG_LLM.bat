@echo off
REM Test RAG LLM Assistant
echo ==========================================
echo Testing RAG LLM Assistant
echo ==========================================
echo.

REM Check Ollama
echo [1/5] Checking Ollama server...
curl -s http://localhost:11434 >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Ollama is not running
    echo Run: ollama serve
    pause
    exit /b 1
)
echo [OK] Ollama is running
echo.

REM Check Backend
echo [2/5] Checking backend server...
curl -s http://localhost:8000/health >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Backend is not running
    echo Run: python -m uvicorn app.main:app --reload --port 8000
    pause
    exit /b 1
)
echo [OK] Backend is running
echo.

REM Check LLM Health
echo [3/5] Checking LLM assistant health...
curl -s http://localhost:8000/api/v1/llm/health
echo.
echo.

REM Initialize Vector Store
echo [4/5] Initializing vector store...
curl -X POST -s http://localhost:8000/api/v1/llm/initialize
echo.
echo.

REM Test Query
echo [5/5] Testing query...
echo Query: "What protocols are monitored?"
echo.
curl -X POST http://localhost:8000/api/v1/llm/query ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"What protocols are monitored?\",\"top_k\":3}"
echo.
echo.

REM Test Streaming Query
echo ==========================================
echo Testing Streaming Query...
echo ==========================================
echo Query: "What is DeFi?"
echo.
curl -X POST http://localhost:8000/api/v1/llm/query/stream ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"What is DeFi?\",\"top_k\":2}"
echo.
echo.

echo ==========================================
echo Tests Complete!
echo ==========================================
echo.
echo If you see responses above, your RAG LLM assistant is working!
echo.
echo Try more queries:
echo - "What are the high-risk protocols?"
echo - "Which protocol has the highest TVL?"
echo - "Explain risk scoring methodology"
echo.
pause


