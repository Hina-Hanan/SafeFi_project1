# Quick Deploy Reference

## Already Done ✅
- [x] Git commit and push successful
- [x] All code pushed to GitHub

## Next Steps (Do This Now)

### 1. Open GCP Console
Go to: https://console.cloud.google.com/compute/instances

### 2. SSH into VM
- Find: `defi-backend-vm`
- Click: **SSH** button
- Opens browser terminal

### 3. Copy and Paste These Commands:

```bash
cd /opt/safefi && \
git pull origin main && \
docker-compose down && \
docker-compose up -d --build && \
sleep 20 && \
docker-compose ps && \
docker-compose logs api --tail=50
```

### 4. Check Scheduler
```bash
curl http://localhost:8000/monitoring/scheduler/status
```

### 5. Verify Production
Open in browser:
- https://safefi.live (frontend)
- https://api.safefi.live/health (backend)

---

## Full Command Block

```bash
cd /opt/safefi && \
git pull origin main && \
docker-compose down && \
docker-compose up -d --build && \
sleep 20 && \
docker-compose exec api alembic upgrade head && \
curl http://localhost:8000/health && \
curl http://localhost:8000/monitoring/scheduler/status
```

---

## Issues?

Check logs:
```bash
docker-compose logs api --tail=100
```

Restart:
```bash
docker-compose restart api
```

