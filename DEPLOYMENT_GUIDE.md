# SafeFi Deployment Guide

This guide covers deployment strategies and CI/CD implementation for the SafeFi DeFi Risk Assessment platform.

## Table of Contents

1. [CI/CD Overview](#cicd-overview)
2. [Containerization](#containerization)
3. [Local Development](#local-development)
4. [Production Deployment](#production-deployment)
5. [Monitoring & Health Checks](#monitoring--health-checks)
6. [Troubleshooting](#troubleshooting)

## CI/CD Overview

### GitHub Actions Workflows

The project includes two main workflows:

#### 1. CI Pipeline (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs:**
- Backend linting and testing (flake8, black, mypy, pytest)
- Frontend linting and building
- Docker image building
- Security scanning with Trivy

#### 2. CD Pipeline (`.github/workflows/deploy.yml`)

**Triggers:**
- Push to `main` branch
- Version tags (v*)
- Manual dispatch

**Jobs:**
- Build and push Docker images to GitHub Container Registry
- Deploy to production server via SSH
- Post-deployment health checks

### Workflow Status Badge

Add to your README:

```markdown
![CI](https://github.com/your-username/safefi/workflows/CI/badge.svg)
![CD](https://github.com/your-username/safefi/workflows/CD/badge.svg)
```

## Containerization

### Backend Docker Image

**File:** `backend/Dockerfile`

**Features:**
- Multi-stage build for optimized size
- Non-root user for security
- Health check endpoint
- Production workers (4 workers)
- Proper dependency management

**Build:**
```bash
docker build -t safefi-backend ./backend
```

### Frontend Docker Image

**File:** `frontend/Dockerfile`

**Features:**
- Multi-stage build
- Nginx for static file serving
- Security headers
- Gzip compression
- Client-side routing support

**Build:**
```bash
docker build -t safefi-frontend ./frontend
```

### Docker Compose

**File:** `docker-compose.yml`

**Services:**
- **db**: PostgreSQL database with health checks
- **mlflow**: Model tracking service
- **api**: FastAPI backend
- **frontend**: React frontend

**Features:**
- Network isolation
- Health checks for all services
- Volume management
- Restart policies
- Environment variable configuration

## Local Development

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local backend development)
- Node.js 20+ (for local frontend development)

### Quick Start

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-username/safefi.git
   cd safefi
   ```

2. **Start Services**
   ```bash
   docker-compose up -d
   ```

3. **Run Migrations**
   ```bash
   docker-compose exec api alembic upgrade head
   ```

4. **Access Services**
   - Frontend: http://localhost
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - MLflow: http://localhost:5000

### Development Environment

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Production Deployment

### Using GitHub Actions (Recommended)

The CD pipeline automatically deploys on push to `main`:

1. **Configure Secrets**
   - Go to GitHub repository settings
   - Add secrets under "Actions"
     - `PROD_HOST`: Production server hostname
     - `PROD_USER`: SSH username
     - `PROD_SSH_KEY`: SSH private key
     - `PROD_PORT`: SSH port (optional)

2. **Push to Main**
   ```bash
   git add .
   git commit -m "Deploy to production"
   git push origin main
   ```

3. **Monitor Deployment**
   - View progress in GitHub Actions tab
   - Check deployment logs

### Manual Deployment

1. **Setup Production Environment**
   ```bash
   cd deploy
   ./setup-production.sh
   ```

2. **Configure Environment**
   ```bash
   # Edit production config
   nano .env.production
   ```

3. **Deploy**
   ```bash
   ./deploy.sh
   ```

4. **Verify Health**
   ```bash
   ./health-check.sh
   ```

### Server Requirements

**Minimum:**
- 2 CPU cores
- 4GB RAM
- 20GB storage
- Docker and Docker Compose

**Recommended:**
- 4 CPU cores
- 8GB RAM
- 50GB storage
- SSD storage
- Ubuntu 22.04 LTS

## Monitoring & Health Checks

### Health Check Endpoints

- **Frontend:** `GET http://localhost/health`
- **Backend:** `GET http://localhost:8000/health`
- **MLflow:** `GET http://localhost:5000/health`

### Health Check Script

```bash
cd deploy
./health-check.sh
```

This checks:
- Frontend accessibility
- Backend API health
- Database connectivity
- MLflow availability

### Log Monitoring

**View Logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f db
```

**Application Logs:**
```bash
# Backend logs
docker exec safefi-api tail -f /app/logs/app.log

# Frontend logs
docker logs safefi-frontend -f
```

### Performance Monitoring

**Container Stats:**
```bash
docker stats safefi-api safefi-frontend safefi-db
```

**Database Size:**
```bash
docker exec safefi-db psql -U defi_user -c "SELECT pg_size_pretty(pg_database_size('defi_risk_assessment'));"
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution:**
```bash
# Change port in .env.production
API_PORT=8001

# Restart services
docker-compose up -d
```

#### 2. Database Connection Failed

**Error:** `connection refused to database`

**Solution:**
```bash
# Check database is running
docker ps | grep postgres

# Restart database
docker-compose restart db

# Check connection
docker exec safefi-db pg_isready -U defi_user
```

#### 3. Out of Memory

**Error:** Container keeps restarting

**Solution:**
```bash
# Reduce workers in backend/Dockerfile
# Change from 4 workers to 2
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# Rebuild
docker-compose up -d --build
```

#### 4. Frontend Not Loading

**Error:** 404 on client-side routes

**Solution:**
- Ensure nginx.conf includes the try_files directive
- Rebuild frontend image
```bash
docker-compose build frontend
docker-compose up -d frontend
```

### Debugging

**Interactive Container Access:**
```bash
# Backend shell
docker exec -it safefi-api bash

# Database shell
docker exec -it safefi-db psql -U defi_user

# Frontend shell
docker exec -it safefi-frontend sh
```

**Check Environment Variables:**
```bash
docker exec safefi-api env
```

**Database Debugging:**
```bash
# Connect to database
docker exec -it safefi-db psql -U defi_user -d defi_risk_assessment

# List tables
\dt

# Check recent queries
SELECT * FROM pg_stat_activity WHERE datname = 'defi_risk_assessment';
```

## Security Best Practices

1. **Use HTTPS in Production**
   - Configure nginx with SSL certificates
   - Use Let's Encrypt for free certificates

2. **Rotate Secrets Regularly**
   - Update passwords monthly
   - Use secret management tools

3. **Network Security**
   - Use firewall rules
   - Restrict SSH access
   - Enable fail2ban

4. **Container Security**
   - Run as non-root user (already configured)
   - Keep base images updated
   - Scan for vulnerabilities regularly

5. **Data Protection**
   - Enable database backups
   - Encrypt sensitive data
   - Use environment variables for secrets

## Backup & Recovery

### Database Backup

```bash
# Create backup
docker exec safefi-db pg_dump -U defi_user defi_risk_assessment > backup_$(date +%Y%m%d).sql

# Restore from backup
docker exec -i safefi-db psql -U defi_user defi_risk_assessment < backup_20240101.sql
```

### Automated Backups

Create a cron job for daily backups:

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * docker exec safefi-db pg_dump -U defi_user defi_risk_assessment > /backups/safefi_$(date +\%Y\%m\%d).sql
```

## Scaling

### Horizontal Scaling

Add more backend workers:

```yaml
# docker-compose.yml
services:
  api:
    deploy:
      replicas: 3
```

### Vertical Scaling

Increase container resources:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

## Additional Resources

- [CICD.md](CICD.md) - Detailed CI/CD documentation
- [deploy/README.md](deploy/README.md) - Deployment scripts
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
