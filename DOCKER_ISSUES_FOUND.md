# Docker Containerization Issues Found

## Issues Identified

### 1. Critical: Backend Dockerfile Running as Non-Root User
**Issue:** Line 43 in `backend/Dockerfile` switches to non-root user BUT:
- Line 40 sets `PATH=/root/.local/bin` which won't be accessible to `appuser`
- The health check (line 50) uses `curl` which requires root access
- User `appuser` may not have permissions for logs and data directories

**Fix:**
```dockerfile
# Line 40 should be:
ENV PATH=/home/appuser/.local/bin:$PATH

# Line 30 should copy to appuser's home:
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Health check should be more permissive or use Python:
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
```

### 2. Moderate: Frontend Health Check Missing in nginx.conf
**Issue:** `frontend/Dockerfile` health check references `/health` but it exists (line 38-43 in nginx.conf)
- This is actually correct, no fix needed

### 3. Critical: Missing Environment Variables in docker-compose.yml
**Issue:** The docker-compose.yml is missing SMTP credentials environment variables:
- Lines 64-66 show SMTP_HOST, SMTP_PORT but missing:
  - SMTP_USER
  - SMTP_PASSWORD
  - EMAIL_FROM
  - EMAIL_FROM_NAME

### 4. Critical: CORS Configuration Issue
**Issue:** Line 59 in docker-compose.yml has:
```yaml
CORS_ORIGINS: ${CORS_ORIGINS:-http://localhost:5173,http://localhost:80}
```
Should be:
```yaml
CORS_ORIGINS: ${CORS_ORIGINS:-https://safefi.live}
```

### 5. Minor: Database Name Mismatch
**Issue:** docker-compose.yml uses `defi_risk_assessment` but the codebase uses `defi_risk`

### 6. Critical: Missing Entrypoint Script
**Issue:** Backend has no entrypoint to handle:
- Database migrations before app starts
- Wait for database to be ready
- Proper signal handling

## Recommended Fixes

### Fix 1: Correct Backend Dockerfile User Permissions

```dockerfile
# Line 30: Copy with correct ownership
COPY --from=builder /root/.local /home/appuser/.local

# Line 40: Use appuser's local bin
ENV PATH=/home/appuser/.local/bin:$PATH

# Line 50: Use Python-based health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
```

### Fix 2: Add Entrypoint Script for Backend

Create `backend/docker-entrypoint.sh`:
```bash
#!/bin/bash
set -e

# Wait for database
until pg_isready -h db -U ${POSTGRES_USER:-defi_user}; do
  echo "Waiting for database..."
  sleep 2
done

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Update Dockerfile CMD:
```dockerfile
# After line 42, before USER:
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh
RUN chown appuser:appuser /app/docker-entrypoint.sh

# Line 53: Use entrypoint
CMD ["/app/docker-entrypoint.sh"]
```

### Fix 3: Update docker-compose.yml Environment Variables

Add to api service (after line 66):
```yaml
    environment:
      # ... existing vars ...
      SMTP_USER: ${SMTP_USER}
      SMTP_PASSWORD: ${SMTP_PASSWORD}
      EMAIL_FROM: ${EMAIL_FROM}
      EMAIL_FROM_NAME: ${EMAIL_FROM_NAME}
```

Fix CORS (line 59):
```yaml
      CORS_ORIGINS: ${CORS_ORIGINS:-https://safefi.live}
```

### Fix 4: Correct Database Name

Change line 16 in docker-compose.yml:
```yaml
      POSTGRES_DB: ${POSTGRES_DB:-defi_risk}
```

And line 55:
```yaml
      DATABASE_URL: postgresql+psycopg2://${POSTGRES_USER:-defi_user}:${POSTGRES_PASSWORD:-usersafety}@db:5432/defi_risk
```

## Priority

1. **HIGH PRIORITY:** Fix user permissions in backend Dockerfile
2. **HIGH PRIORITY:** Add SMTP environment variables
3. **MEDIUM PRIORITY:** Fix CORS origins
4. **MEDIUM PRIORITY:** Add entrypoint script
5. **LOW PRIORITY:** Fix database name consistency

## Testing Checklist

After fixes, verify:
- [ ] Backend container starts without permission errors
- [ ] Health check works
- [ ] Database connection works
- [ ] Email service can connect to SMTP
- [ ] CORS allows requests from safefi.live
- [ ] Frontend connects to backend API

