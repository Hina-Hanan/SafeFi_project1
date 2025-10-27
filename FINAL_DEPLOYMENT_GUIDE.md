# Final Deployment Guide - SafeFi Live

## ✅ Issues Fixed

1. **Backend User Permissions** - Fixed PATH and pip package location for non-root user
2. **Database Migrations** - Added entrypoint script that waits for DB and runs migrations
3. **Health Checks** - Changed from curl to Python-based check (avoids permission issues)
4. **SMTP Configuration** - Added missing environment variables
5. **CORS Origins** - Updated for production environment
6. **Database Name** - Fixed mismatch between docker-compose and code

## 🚀 Deployment Commands

### SSH into GCP VM

1. Go to: https://console.cloud.google.com/compute/instances
2. Find: `defi-backend-vm` (IP: 34.55.12.211)
3. Click: **SSH** button

### Run These Commands

```bash
# Navigate to project
cd /opt/safefi

# Pull latest code
git pull origin main

# Check environment variables
cat .env | grep -E "DATABASE_URL|SMTP_|ENVIRONMENT"

# Stop services
docker-compose down

# Rebuild with new Dockerfile fixes
docker-compose up -d --build

# Wait for services to start
sleep 20

# Check service status
docker-compose ps

# Check API logs
docker-compose logs api --tail=100

# Test health endpoint
curl http://localhost:8000/health

# Test scheduler
curl http://localhost:8000/monitoring/scheduler/status
```

## 🔍 Verification

### Check Production URLs

1. **Frontend:** https://safefi.live
2. **Backend Health:** https://api.safefi.live/health
3. **API Protocols:** https://api.safefi.live/api/v1/protocols?limit=5
4. **Scheduler:** https://api.safefi.live/monitoring/scheduler/status

### Monitor Logs

```bash
# Follow API logs
docker-compose logs -f api

# Check specific errors
docker-compose logs api | grep -i error
```

## 📋 Environment Variables Needed on VM

Ensure these are in `/opt/safefi/.env`:

```bash
# Database
POSTGRES_USER=defi_user
POSTGRES_PASSWORD=usersafety
POSTGRES_DB=defi_risk

# Production Environment
ENVIRONMENT=production
CORS_ORIGINS=https://safefi.live

# Email Settings
EMAIL_ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-gmail@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-gmail@gmail.com
EMAIL_FROM_NAME=SafeFi Alert System

# API Configuration
API_PORT=8000
LOG_LEVEL=INFO
```

## 🐛 Troubleshooting

### If containers don't start:

```bash
# Check logs
docker-compose logs --tail=100

# Restart failed services
docker-compose restart api

# Rebuild if needed
docker-compose down
docker-compose up -d --build
```

### If database connection fails:

```bash
# Check database logs
docker-compose logs db

# Test connection
docker-compose exec api python -c "from app.database.connection import get_db; next(get_db())"
```

### If email alerts don't work:

```bash
# Test email configuration
curl -X POST http://localhost:8000/monitoring/alerts/test/your-email@gmail.com

# Check logs for SMTP errors
docker-compose logs api | grep -i smtp
```

### If frontend can't reach backend:

```bash
# Verify CORS settings
docker-compose exec api env | grep CORS

# Test from frontend container
docker-compose exec frontend curl http://api:8000/health
```

## 🎯 Success Indicators

- [ ] All containers running (`docker-compose ps` shows all "Up")
- [ ] API health endpoint returns 200
- [ ] Frontend loads at https://safefi.live
- [ ] Scheduler status shows "running": true
- [ ] Database migrations completed
- [ ] Email test sends successfully

## 📊 What Was Fixed

### Before (Issues):
- Non-root user couldn't access pip packages
- Health check required curl (not available)
- Missing SMTP credentials
- Wrong database name
- No migration handling

### After (Fixed):
- ✅ Correct PATH for appuser
- ✅ Python-based health check
- ✅ All SMTP variables present
- ✅ Correct database name (defi_risk)
- ✅ Entrypoint handles migrations and DB wait
- ✅ Proper permissions for all directories

## 🔄 Rollback if Needed

```bash
# Go back to previous commit
cd /opt/safefi
git log --oneline -5  # Find commit before fixes
git checkout <previous-commit-hash>

# Restart services
docker-compose down
docker-compose up -d --build
```

## ✅ You're Ready to Deploy!

The Docker configuration is now production-ready. Simply SSH into your GCP VM and run the deployment commands above.

