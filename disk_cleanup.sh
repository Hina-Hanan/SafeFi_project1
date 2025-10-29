# Disk Space Cleanup Commands for GCP VM

# Run these commands on your GCP VM (SSH):

# 1. Check disk space
df -h

# 2. Check Docker disk usage
docker system df

# 3. Check what's using space
du -sh /var/lib/docker/* 2>/dev/null | sort -h | tail -10

# 4. Clean Docker aggressively
docker system prune -a --volumes -f

# 5. Stop all containers
docker compose down

# 6. Remove all unused images
docker image prune -a -f

# 7. Remove build cache
docker builder prune -a -f

# 8. Clean apt cache
sudo apt-get clean
sudo apt-get autoremove -y

# 9. Clean old logs
sudo journalctl --vacuum-time=3d

# 10. Check space again
df -h

# If still low on space, you have options:
# Option A: Use slim build (no LLM) - smaller
# Option B: Increase VM disk size
# Option C: Use multi-stage build optimization

