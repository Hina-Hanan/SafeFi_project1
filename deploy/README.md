# SafeFi Deployment Guide

This directory contains deployment scripts and configurations for the SafeFi DeFi Risk Assessment platform.

## Quick Start

### 1. Initial Setup

```bash
# Navigate to deploy directory
cd deploy

# Run setup script
./setup-production.sh
```

### 2. Configure Environment

Edit `.env.production` with your production values:

```bash
nano .env.production
```

### 3. Deploy

```bash
./deploy.sh
```

### 4. Verify Deployment

```bash
./health-check.sh
```

## Scripts

### `setup-production.sh`

Sets up the production environment:
- Creates necessary directories
- Creates `.env.production` file
- Configures permissions

### `deploy.sh`

Deploys the application:
- Pulls latest Docker images
- Starts all services
- Runs database migrations
- Performs health checks

### `health-check.sh`

Verifies all services are healthy:
- Frontend health check
- Backend API health check
- Database connection check
- MLflow health check

### `docker-compose.prod.yml`

Production Docker Compose configuration:
- PostgreSQL database
- MLflow service
- Backend API
- Frontend application

## Manual Deployment

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart specific service
docker-compose restart api
```

### Environment Variables

Required environment variables:

```bash
# Database
POSTGRES_USER=defi_user
POSTGRES_PASSWORD=<secure_password>
POSTGRES_DB=defi_risk_assessment

# API
API_PORT=8000
CORS_ORIGINS=https://safefi.live
# MLflow
MLFLOW_PORT=5000

# Frontend
FRONTEND_PORT=80
```

## Monitoring

### Check Service Status

```bash
# View all containers
docker ps

# View specific service logs
docker logs safefi-api -f
docker logs safefi-frontend -f
docker logs safefi-db -f
```

### Health Endpoints

- Frontend: http://localhost/health
- Backend: http://localhost:8000/health
- MLflow: http://localhost:5000/health

### Database Access

```bash
# Connect to database
docker exec -it safefi-db psql -U defi_user -d defi_risk_assessment

# Run migration
docker exec safefi-api alembic upgrade head
```

## Maintenance

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild images
docker-compose build

# Restart services
docker-compose up -d
```

### Backup Database

```bash
# Backup
docker exec safefi-db pg_dump -U defi_user defi_risk_assessment > backup.sql

# Restore
docker exec -i safefi-db psql -U defi_user defi_risk_assessment < backup.sql
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100 api
```

## Troubleshooting

### Services Won't Start

```bash
# Check Docker status
docker ps -a

# View container logs
docker logs safefi-api

# Check Docker Compose logs
docker-compose logs
```

### Database Connection Issues

```bash
# Check database is running
docker ps | grep postgres

# Test connection
docker exec safefi-db pg_isready -U defi_user
```

### Port Conflicts

Edit `.env.production` to use different ports:

```bash
API_PORT=8001
MLFLOW_PORT=5001
FRONTEND_PORT=8080
```

### Reset Everything

```bash
# Stop and remove all containers
docker-compose down -v

# Remove volumes
docker volume rm safefi_pgdata safefi_mlruns

# Start fresh
docker-compose up -d
```

## Production Checklist

- [ ] Environment variables configured
- [ ] Database backed up
- [ ] SSL certificates installed
- [ ] Security secrets rotated
- [ ] Monitoring configured
- [ ] Error tracking enabled
- [ ] Backup strategy implemented
- [ ] Disaster recovery plan tested

## Security Considerations

1. **Use strong passwords** for database and services
2. **Enable HTTPS** for production deployment
3. **Rotate secrets** regularly
4. **Monitor logs** for suspicious activity
5. **Keep dependencies updated**
6. **Use firewall rules** to restrict access
7. **Backup data** regularly
8. **Test disaster recovery** procedures

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Review documentation: `../CICD.md`
- Check health: `./health-check.sh`
