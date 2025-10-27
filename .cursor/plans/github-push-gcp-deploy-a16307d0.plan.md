<!-- a16307d0-986b-4eba-b40f-26e30e8f1262 e415e2b9-4331-4afd-b158-4a5ada25b0c2 -->
# GitHub Push and GCP Manual Deployment Plan

## Overview

Commit all changes, push to GitHub, then SSH into GCP VM (defi-backend-vm at 34.55.12.211) to pull changes and restart services manually.

## Phase 1: Git Commit and Push

### Files to Commit

**Modified Backend Files:**

- `backend/app/services/email_alert_service.py` - Email format improvements
- `backend/app/database/models.py` - UUID fix for EmailSubscriber
- `backend/app/api/v1/monitoring.py` - Added get_email_service import
- `backend/app/api/v1/email_alerts.py` - Alert endpoints
- `backend/app/startup.py` - Async scheduler integration
- `backend/requirements.txt` - Added apscheduler

**New Backend Services:**

- `backend/app/services/automated_scheduler.py` - 15-30 min randomized updates
- `backend/app/services/subscriber_alert_service.py` - Personalized alerts

**Modified Frontend Files:**

- `frontend/src/services/api.ts` - Fixed fetchProtocols response handling
- `frontend/src/components/ActiveRiskAlerts.tsx`
- `frontend/src/components/RiskThresholdSettings.tsx`

**New Infrastructure:**

- `.github/` - CI/CD workflows
- `docker-compose.yml` - Updated
- `backend/Dockerfile`, `frontend/Dockerfile` - Enhanced
- `frontend/nginx.conf` - New
- `.dockerignore`, `backend/.dockerignore`, `frontend/.dockerignore`

**Documentation:**

- `AUTOMATED_ALERTS_SETUP.md`
- `EMAIL_FORMAT_IMPROVEMENTS.md`
- `FRONTEND_BACKEND_CONNECTION.md`
- `CICD.md`, `DEPLOYMENT_GUIDE.md`, etc.

### Git Commands

```bash
# Add all modified and new files
git add -A

# Commit with descriptive message
git commit -m "feat: email alerts, automated scheduler, frontend fixes

- Improved email format with dynamic URLs (safefi.live/localhost)
- Added automated scheduler (15-30 min intervals)
- Fixed EmailSubscriber UUID type mismatch
- Added subscriber alert service with personalized thresholds
- Fixed frontend fetchProtocols response handling
- Enhanced Dockerfiles and CI/CD workflows
- Updated documentation"

# Push to GitHub
git push origin main
```

## Phase 2: SSH to GCP VM

### Connection Details

- **VM Instance:** defi-backend-vm
- **IP Address:** 34.55.12.211
- **Method:** SSH via browser (GCP Console)

### SSH Access Steps

1. Go to GCP Console → Compute Engine → VM Instances
2. Find `defi-backend-vm`
3. Click "SSH" button (opens browser terminal)

## Phase 3: Manual Deployment on VM

### Step-by-Step Commands

```bash
# 1. Navigate to project directory
cd /opt/safefi

# 2. Check current status
git status
docker ps

# 3. Pull latest code from GitHub
git fetch origin
git pull origin main

# 4. Check if .env file exists and has required variables
cat .env | grep -E "DATABASE_URL|SMTP_|ENVIRONMENT"

# 5. Backup current database (optional but recommended)
docker-compose exec -T db pg_dump -U postgres defi_risk > backup_$(date +%Y%m%d_%H%M%S).sql

# 6. Stop current services
docker-compose down

# 7. Rebuild and restart services
docker-compose up -d --build

# 8. Wait for services to start
sleep 15

# 9. Check service status
docker-compose ps
docker-compose logs --tail=50 api

# 10. Run database migrations (if any)
docker-compose exec api alembic upgrade head

# 11. Restart services to apply all changes
docker-compose restart api

# 12. Verify health
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/protocols?limit=3

# 13. Check scheduler is running
curl http://localhost:8000/monitoring/scheduler/status

# 14. Test email alert (replace with your email)
curl -X POST http://localhost:8000/monitoring/alerts/test/hinahanan003@gmail.com
```

## Phase 4: Verification

### Check These Endpoints

```bash
# Backend health
curl https://api.safefi.live/health

# Protocols endpoint
curl https://api.safefi.live/api/v1/protocols?limit=5

# Scheduler status
curl https://api.safefi.live/monitoring/scheduler/status

# Frontend (in browser)
# https://safefi.live
```

### Check Logs for Errors

```bash
# Backend logs
docker-compose logs -f api --tail=100

# Database logs
docker-compose logs db --tail=50

# All services
docker-compose logs --tail=100
```

## Important Notes

1. **Environment Variables:** Ensure `.env` on VM has:

   - `ENVIRONMENT=production`
   - `CORS_ORIGINS=https://safefi.live`
   - SMTP settings for email alerts
   - Database credentials

2. **Database Migration:** The UUID fix might require migration. If errors occur:
   ```bash
   docker-compose exec api python -m alembic revision --autogenerate -m "Fix EmailSubscriber UUID type"
   docker-compose exec api alembic upgrade head
   ```

3. **Nginx/Frontend:** If using separate Nginx for frontend routing, restart it:
   ```bash
   sudo systemctl restart nginx
   ```

4. **Firewall:** Ensure ports 80, 443, 8000 are open in GCP firewall rules

## Rollback Plan (if needed)

```bash
# Stop services
docker-compose down

# Checkout previous commit
git log --oneline -10  # Find previous commit hash
git checkout <previous-commit-hash>

# Restart services
docker-compose up -d --build
```

## Success Criteria

- [ ] Git push successful
- [ ] SSH connection established
- [ ] Code pulled on VM
- [ ] Services restarted without errors
- [ ] Health endpoints return 200
- [ ] Frontend loads at https://safefi.live
- [ ] Scheduler status shows running
- [ ] Test email received successfully

### To-dos

- [ ] Fix docker-compose.yml SMTP_PASSWORD and EMAIL_ALERTS_ENABLED, remove duplicate networks
- [ ] Create .env file in project root with production variables
- [ ] Ensure .env is in .gitignore
- [ ] Remove automated deployment jobs from .github/workflows/deploy.yml
- [ ] Create DEPLOYMENT.md with manual deployment steps
- [ ] Create VM_SETUP.md with VM environment documentation
- [ ] Create .env file on VM at /var/lib/postgresql/SafeFi_project1/
- [ ] Push changes to GitHub and deploy to VM, verify all services