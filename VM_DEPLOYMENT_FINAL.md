# Final VM Deployment Commands

Run these commands ON THE GCP VM (via SSH browser terminal):

## Step 1: Clean Up Everything

```bash
# Kill any processes using port 8000
sudo pkill -f uvicorn
sudo killall python3

# Stop all containers
sudo docker compose down -v

# Clean up Docker (frees up space)
sudo docker system prune -a --volumes -f

# Clean up system packages
sudo apt-get clean
sudo apt-get autoremove -y

# Check available space
df -h
```

## Step 2: Pull Latest Code

```bash
cd /var/lib/postgresql/SafeFi_project1

# Stash any local changes
git stash

# Pull latest code
git pull origin main

# Verify backend/requirements.txt exists
ls -la backend/requirements.txt
cat backend/requirements.txt | head -20
```

## Step 3: Rebuild and Deploy

```bash
# Rebuild with new Dockerfile (no cache)
sudo docker compose build api --no-cache

# Start all services
sudo docker compose up -d

# Wait for services to start
sleep 30

# Check status
sudo docker compose ps
```

## Step 4: Create Database Tables

```bash
# Create tables using Python
sudo docker compose exec api python << 'EOF'
from sqlalchemy import create_engine
from app.database.connection import get_db_config
from app.db.base import Base
import app.database.models
import app.db.models

db_config = get_db_config()
engine = create_engine(db_config["url"])
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully!")
EOF
```

## Step 5: Verify Deployment

```bash
# Check API logs
sudo docker compose logs api --tail=100

# Test health endpoint
curl http://localhost:8000/health

# Test protocols
curl http://localhost:8000/api/v1/protocols?limit=5

# Check scheduler
curl http://localhost:8000/monitoring/scheduler/status
```

## Troubleshooting

If "No space left" error continues:

```bash
# Check what's taking space
sudo du -sh /* 2>/dev/null | sort -h | tail -20

# Remove old Docker images manually
sudo docker images
sudo docker rmi $(sudo docker images -q)

# Remove unused containers
sudo docker rm $(sudo docker ps -aq) 2>/dev/null
```

If build still fails:

```bash
# Try building with more verbose output
sudo docker compose build api --progress=plain --no-cache 2>&1 | tee build.log

# Check the log file
cat build.log | grep -i error
```

