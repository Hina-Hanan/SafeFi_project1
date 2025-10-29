# Docker Deployment Guide - Production Ready with LLM

This guide covers deploying the DeFi Risk Assessment backend with Docker, including LLM/RAG capabilities.

## 📋 Prerequisites

- Docker and Docker Compose installed
- Git repository cloned
- Environment variables configured (see `.env.example`)

## 🚀 Quick Start

### 1. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your production values
nano .env
```

**Key variables to set:**
- `POSTGRES_PASSWORD`: Strong password for database
- `DATABASE_URL`: Connection string (Docker: use `db` as hostname)
- `CORS_ORIGINS`: Your frontend domain(s) from GCS
- `SMTP_*`: Email configuration if using alerts

### 2. Deploy Without LLM (Slim API)

```bash
# Build and start services
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f api
```

### 3. Deploy With LLM (Full Stack)

**Prerequisites:**
- Ollama installed and running on host machine
- Model downloaded: `ollama pull tinyllama`

```bash
# Build with LLM dependencies
docker compose -f docker-compose.yml -f docker-compose.llm.yml up -d --build

# Check status
docker compose ps

# Verify LLM dependencies
docker compose exec api python -c "import langchain, chromadb, sentence_transformers; print('✅ LLM deps OK')"
```

## 🔧 Configuration Details

### Database Connection

**Inside Docker containers:** Use `db` as hostname (Docker service name)
```env
DATABASE_URL=postgresql+psycopg2://defi_user:password@db:5432/defi_risk_assessment
```

**Local development:** Use `localhost`
```env
DATABASE_URL=postgresql+psycopg2://defi_user:password@localhost:5432/defi_risk_assessment
```

### LLM Configuration

**Without Docker (local dev):**
```env
OLLAMA_BASE_URL=http://localhost:11434
```

**With Docker (Windows/macOS):**
```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

**With Docker (Linux/GCP):**
- `docker-compose.llm.yml` automatically adds `extra_hosts` for Linux compatibility
- Use `http://host.docker.internal:11434` (same as Windows/macOS)

### CORS Configuration

For GCS frontend deployment:
```env
CORS_ORIGINS=https://storage.googleapis.com,https://YOUR_BUCKET_NAME.storage.googleapis.com
```

For custom domain:
```env
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 📦 Docker Services

### API Service (`safefi-api`)
- **Image:** Built from `backend/Dockerfile`
- **Port:** 8000
- **Health Check:** `/health` endpoint
- **Volumes:**
  - `./backend/models:/app/models` - ML models
  - `./backend/data:/app/data` - Vector store data
  - `./backend/logs:/app/logs` - Application logs

### Database Service (`safefi-db`)
- **Image:** `postgres:15`
- **Port:** 5432
- **Volumes:** `pgdata` (persistent storage)
- **Database:** `defi_risk_assessment`

## 🛠️ Common Commands

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f db

# Last 100 lines
docker compose logs --tail=100 api
```

### Restart Services
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart api
```

### Stop/Start Services
```bash
# Stop
docker compose down

# Start (preserves volumes)
docker compose up -d

# Stop and remove volumes (⚠️ destroys data)
docker compose down -v
```

### Access Container Shell
```bash
# API container
docker compose exec api bash

# Database container
docker compose exec db psql -U defi_user -d defi_risk_assessment
```

### Health Checks
```bash
# Check API health
curl http://localhost:8000/health

# Check database from container
docker compose exec db pg_isready -U defi_user
```

## 🚀 GCP Deployment

### 1. Prepare VM
```bash
# SSH into GCP VM
ssh your-user@YOUR_VM_IP

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone Repository
```bash
git clone YOUR_REPO_URL
cd main-project
```

### 3. Configure Environment
```bash
cp .env.example .env
nano .env  # Update with production values
```

### 4. Install Ollama (for LLM)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull tinyllama

# Start Ollama service
ollama serve
```

### 5. Deploy with LLM
```bash
# Build and start
docker compose -f docker-compose.yml -f docker-compose.llm.yml up -d --build

# Verify
docker compose ps
curl http://localhost:8000/health
```

### 6. Configure Firewall
```bash
# Allow port 8000
gcloud compute firewall-rules create allow-backend-api \
  --allow tcp:8000 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow backend API access"
```

## 🔍 Troubleshooting

### Database Connection Issues
```bash
# Check database logs
docker compose logs db

# Test connection from API container
docker compose exec api python -c "from app.database.connection import ENGINE; ENGINE.connect()"
```

### LLM Connection Issues
```bash
# Verify Ollama is running on host
curl http://localhost:11434/api/tags

# Test from container
docker compose exec api curl http://host.docker.internal:11434/api/tags
```

### Container Won't Start
```bash
# Check logs
docker compose logs api

# Check if port is in use
sudo netstat -tlnp | grep 8000

# Rebuild without cache
docker compose build --no-cache api
```

### Out of Disk Space
```bash
# Clean Docker
docker system prune -a --volumes

# Check disk usage
df -h
docker system df
```

## 📊 Monitoring

### Health Endpoints
- **API Health:** `http://localhost:8000/health`
- **Scheduler Status:** `http://localhost:8000/monitoring/scheduler/status`
- **LLM Health (if enabled):** `http://localhost:8000/llm/health`

### Log Files
Logs are stored in `./backend/logs/` (mounted as volume).

## 🔐 Security Best Practices

1. **Strong Passwords:** Use complex passwords for `POSTGRES_PASSWORD`
2. **Environment Variables:** Never commit `.env` to git
3. **CORS:** Restrict `CORS_ORIGINS` to your frontend domains only
4. **Firewall:** Limit access to port 8000 to trusted IPs (production)
5. **Secrets:** Use secret management (GCP Secret Manager) for production

## 📝 Notes

- **Frontend:** Deployed separately to GCS (not in Docker)
- **Database:** Persistent data stored in Docker volume `pgdata`
- **Models:** ML models stored in `./backend/models/` (volume mount)
- **Vector Store:** RAG vector store in `./backend/data/vectorstore/`

## 🆘 Support

For issues:
1. Check logs: `docker compose logs -f`
2. Verify environment: `docker compose config`
3. Test health: `curl http://localhost:8000/health`
4. Review this guide for common issues

