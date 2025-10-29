# Production Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. Environment Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Set strong `POSTGRES_PASSWORD`
- [ ] Configure `DATABASE_URL` (use `db` hostname for Docker)
- [ ] Set `CORS_ORIGINS` for your frontend domain(s)
- [ ] Configure email settings if using alerts
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure `LOG_LEVEL=INFO` (or `WARNING` for production)

### 2. LLM Configuration (if using LLM)
- [ ] Install Ollama on host machine
- [ ] Pull model: `ollama pull tinyllama`
- [ ] Verify Ollama is running: `curl http://localhost:11434/api/tags`
- [ ] Set `OLLAMA_BASE_URL` appropriately:
  - Docker: `http://host.docker.internal:11434`
  - Local: `http://localhost:11434`
- [ ] Set `RAG_ENABLED=true` in `.env` or compose override

### 3. Security
- [ ] Strong database password set
- [ ] `.env` file not committed to git (check `.gitignore`)
- [ ] CORS origins restricted to frontend domains only
- [ ] Firewall rules configured (GCP: allow port 8000)
- [ ] Review and update security group rules

### 4. Frontend Configuration
- [ ] Frontend `api.ts` points to correct backend URL
- [ ] Frontend built and deployed to GCS
- [ ] CORS configured to allow frontend domain

## 🚀 Deployment Steps

### Step 1: Build Docker Images

**Without LLM (Slim):**
```bash
docker compose build
```

**With LLM (Full):**
```bash
docker compose -f docker-compose.yml -f docker-compose.llm.yml build
```

### Step 2: Start Services

**Without LLM:**
```bash
docker compose up -d
```

**With LLM:**
```bash
docker compose -f docker-compose.yml -f docker-compose.llm.yml up -d
```

### Step 3: Verify Deployment

```bash
# Check container status
docker compose ps

# Check API health
curl http://localhost:8000/health

# Check logs
docker compose logs -f api

# Verify LLM (if enabled)
docker compose exec api python -c "import langchain; print('✅ LLM OK')"
```

### Step 4: Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Protocols list
curl http://localhost:8000/protocols

# Scheduler status
curl http://localhost:8000/monitoring/scheduler/status

# LLM health (if enabled)
curl http://localhost:8000/llm/health
```

## 🔍 Post-Deployment Verification

### Database
- [ ] Tables created automatically (check logs)
- [ ] Protocols seeded (if `SEED_PROTOCOLS=true`)
- [ ] Can connect: `docker compose exec db psql -U defi_user -d defi_risk_assessment`

### API
- [ ] Health endpoint returns 200
- [ ] All endpoints accessible
- [ ] Scheduler running (check logs)
- [ ] CORS working (test from frontend)

### LLM (if enabled)
- [ ] LLM dependencies installed
- [ ] Vector store initialized
- [ ] LLM endpoints visible in `/docs`
- [ ] Can connect to Ollama from container

### Monitoring
- [ ] Logs accessible: `docker compose logs -f`
- [ ] Health checks passing
- [ ] No errors in logs

## 📊 Production Optimizations

### Resource Limits (Optional)
Add to `docker-compose.yml`:
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Log Rotation
Logs are stored in `./backend/logs/`. Configure log rotation:
```bash
# Add to crontab or systemd timer
find ./backend/logs -name "*.log" -mtime +7 -delete
```

### Database Backups
```bash
# Backup script
docker compose exec db pg_dump -U defi_user defi_risk_assessment > backup_$(date +%Y%m%d).sql
```

## 🛠️ Troubleshooting

### Container Won't Start
- Check logs: `docker compose logs api`
- Verify environment: `docker compose config`
- Check disk space: `df -h`

### Database Connection Issues
- Verify database is healthy: `docker compose ps db`
- Check connection string in `.env`
- Test connection: `docker compose exec api python -c "from app.database.connection import ENGINE; ENGINE.connect()"`

### LLM Not Working
- Verify Ollama running: `curl http://localhost:11434/api/tags`
- Check from container: `docker compose exec api curl http://host.docker.internal:11434/api/tags`
- Verify dependencies: `docker compose exec api python -c "import langchain"`

### Port Already in Use
```bash
# Find process using port 8000
sudo lsof -i :8000
# Or
sudo netstat -tlnp | grep 8000

# Kill process or change port in .env
```

## 📝 Maintenance

### Regular Updates
```bash
# Pull latest code
git pull

# Rebuild and restart
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Log Monitoring
```bash
# Real-time logs
docker compose logs -f api

# Search logs
docker compose logs api | grep ERROR

# Export logs
docker compose logs api > api.log
```

## ✅ Production Ready Checklist

All items checked? Your deployment is production-ready! 🎉

- [ ] Environment configured
- [ ] Security hardened
- [ ] All services running
- [ ] Health checks passing
- [ ] Frontend connected
- [ ] Logs monitored
- [ ] Backups configured
- [ ] Documentation reviewed

