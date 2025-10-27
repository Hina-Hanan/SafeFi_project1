# GCP Deployment Commands

## SSH Connection

1. Go to https://console.cloud.google.com
2. Navigate to Compute Engine → VM Instances
3. Find `defi-backend-vm` (IP: 34.55.12.211)
4. Click the **SSH** button (opens browser terminal)

---

## Deployment Commands

Copy and run these commands in the SSH browser terminal:

```bash
# 1. Navigate to project directory
cd /opt/safefi

# 2. Check current status
echo "=== Git Status ==="
git status
echo ""
echo "=== Docker Containers ==="
docker ps

# 3. Pull latest code from GitHub
echo "=== Pulling Latest Code ==="
git fetch origin
git pull origin main

# 4. Check environment variables
echo "=== Environment Check ==="
cat .env | grep -E "DATABASE_URL|SMTP_|ENVIRONMENT|CORS_ORIGINS"

# 5. Backup database (optional but recommended)
echo "=== Backing up database ==="
docker-compose exec -T db pg_dump -U postgres defi_risk > backup_$(date +%Y%m%d_%H%M%S).sql
echo "✓ Backup created"

# 6. Stop current services
echo "=== Stopping services ==="
docker-compose down

# 7. Rebuild and restart services
echo "=== Rebuilding and starting services ==="
docker-compose up -d --build

# 8. Wait for services to start
echo "=== Waiting for services to start (15 seconds) ==="
sleep 15

# 9. Check service status
echo "=== Service Status ==="
docker-compose ps
echo ""
echo "=== API Logs ==="
docker-compose logs --tail=50 api

# 10. Run database migrations
echo "=== Running database migrations ==="
docker-compose exec api alembic upgrade head

# 11. Restart API to apply all changes
echo "=== Restarting API ==="
docker-compose restart api

# 12. Wait and verify health
echo "=== Waiting 10 seconds for services to be ready ==="
sleep 10

echo "=== Health Check ==="
curl -f http://localhost:8000/health || echo "❌ Health check failed"

echo "=== Testing Protocols Endpoint ==="
curl -s http://localhost:8000/api/v1/protocols?limit=3 | head -50

# 13. Check scheduler status
echo "=== Scheduler Status ==="
curl -s http://localhost:8000/monitoring/scheduler/status

# 14. Test email alert
echo "=== Testing Email Alert ==="
curl -X POST http://localhost:8000/monitoring/alerts/test/hinahanan003@gmail.com

echo ""
echo "✅ Deployment complete!"
```

---

## Troubleshooting

### If services don't start properly:

```bash
# Check logs
docker-compose logs api --tail=100

# Restart specific service
docker-compose restart api

# Rebuild if needed
docker-compose down
docker-compose up -d --build
```

### If database migration fails:

```bash
# Generate new migration
docker-compose exec api alembic revision --autogenerate -m "Fix EmailSubscriber UUID type"

# Apply migration
docker-compose exec api alembic upgrade head
```

### If CORS or API issues:

```bash
# Check .env has correct settings
cat .env | grep CORS

# Edit if needed (use nano or vi)
nano .env

# Restart services after editing
docker-compose restart api
```

---

## Verify Production Endpoints

After deployment, test these URLs in your browser:

1. **Frontend:** https://safefi.live
2. **Backend Health:** https://api.safefi.live/health
3. **API Protocols:** https://api.safefi.live/api/v1/protocols?limit=5
4. **Scheduler Status:** https://api.safefi.live/monitoring/scheduler/status

---

## Success Indicators

- [x] Git push successful
- [ ] Code pulled on VM
- [ ] Services restarted without errors
- [ ] Health endpoint returns 200
- [ ] Frontend loads at https://safefi.live
- [ ] Scheduler status shows running
- [ ] Test email received successfully

