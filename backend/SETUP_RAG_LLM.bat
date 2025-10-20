@echo off
REM Setup RAG-Powered LLM Assistant
echo ==========================================
echo RAG LLM Assistant Setup
echo ==========================================
echo.

REM Check if Ollama is installed
where ollama >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Ollama is not installed!
    echo.
    echo Please install Ollama first:
    echo 1. Run: winget install Ollama.Ollama
    echo 2. Or download from: https://ollama.ai/download
    echo.
    pause
    exit /b 1
)

echo [OK] Ollama is installed
echo.

REM Check if Ollama is running
curl -s http://localhost:11434 >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Ollama server is not running
    echo Starting Ollama in background...
    start /B ollama serve
    timeout /t 3 >nul
)

echo [OK] Ollama server is running
echo.

REM Pull LLM model
echo ==========================================
echo Step 1: Pull LLM Model
echo ==========================================
echo.
echo Select a model to download:
echo 1. Llama 3 (4.7GB) - Recommended
echo 2. Mistral (4.1GB) - Fast alternative
echo 3. DeepSeek Coder (4GB) - Code-focused
echo 4. Phi-3 (2.3GB) - Lightweight
echo 5. Skip (already downloaded)
echo.
set /p model_choice="Enter choice (1-5): "

if "%model_choice%"=="1" (
    echo Pulling Llama 3...
    ollama pull llama3
    set OLLAMA_MODEL=llama3
) else if "%model_choice%"=="2" (
    echo Pulling Mistral...
    ollama pull mistral
    set OLLAMA_MODEL=mistral
) else if "%model_choice%"=="3" (
    echo Pulling DeepSeek Coder...
    ollama pull deepseek-coder
    set OLLAMA_MODEL=deepseek-coder
) else if "%model_choice%"=="4" (
    echo Pulling Phi-3...
    ollama pull phi3
    set OLLAMA_MODEL=phi3
) else (
    echo Skipping model download
    set OLLAMA_MODEL=llama3
)

echo.

REM Pull embedding model
echo ==========================================
echo Step 2: Pull Embedding Model
echo ==========================================
echo.
echo Pulling nomic-embed-text for RAG embeddings...
ollama pull nomic-embed-text

echo.

REM Install Python dependencies
echo ==========================================
echo Step 3: Install Python Dependencies
echo ==========================================
echo.
echo Installing LangChain, sentence-transformers, and vector stores...

pip install langchain==0.1.20 langchain-community==0.0.38 langchain-core==0.1.52 sentence-transformers==2.7.0 chromadb==0.4.24 faiss-cpu==1.8.0 pypdf==4.2.0 python-docx==1.1.0

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.

REM Create .env file
echo ==========================================
echo Step 4: Configure Environment
echo ==========================================
echo.

if exist .env (
    echo .env file already exists
    set /p overwrite="Overwrite? (y/n): "
    if /i not "%overwrite%"=="y" goto skip_env
)

echo Creating .env file...
(
echo # LLM Configuration
echo OLLAMA_BASE_URL=http://localhost:11434
echo OLLAMA_MODEL=%OLLAMA_MODEL%
echo OLLAMA_TEMPERATURE=0.7
echo OLLAMA_EMBEDDING_MODEL=nomic-embed-text
echo.
echo # RAG Configuration
echo RAG_CHUNK_SIZE=500
echo RAG_CHUNK_OVERLAP=50
echo RAG_TOP_K=5
echo VECTOR_STORE_PATH=./data/vectorstore
) > .env

echo [OK] .env file created

:skip_env

echo.

REM Test installation
echo ==========================================
echo Step 5: Test Installation
echo ==========================================
echo.
echo Testing Ollama connection...

curl -s http://localhost:11434 >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Cannot connect to Ollama
    echo Please ensure Ollama is running: ollama serve
    pause
    exit /b 1
)

echo [OK] Ollama is accessible
echo.

REM Summary
echo ==========================================
echo Setup Complete! 
echo ==========================================
echo.
echo Configuration:
echo - LLM Model: %OLLAMA_MODEL%
echo - Embedding Model: nomic-embed-text
echo - Ollama URL: http://localhost:11434
echo.
echo Next Steps:
echo 1. Start backend server:
echo    python -m uvicorn app.main:app --reload --port 8000
echo.
echo 2. Initialize vector store:
echo    curl -X POST http://localhost:8000/api/v1/llm/initialize
echo.
echo 3. Test query:
echo    curl -X POST http://localhost:8000/api/v1/llm/query ^
echo      -H "Content-Type: application/json" ^
echo      -d "{\"query\": \"What protocols are monitored?\"}"
echo.
echo Documentation:
echo - Full Guide: ..\markdowns\RAG_LLM_INTEGRATION.md
echo - Quick Start: ..\markdowns\RAG_QUICK_START.md
echo.
pause


