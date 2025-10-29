#!/bin/bash
set -e

echo "🚀 Starting DeFi Risk Assessment Backend..."
echo "📋 Environment: ${ENVIRONMENT:-production}"
echo "📋 Log Level: ${LOG_LEVEL:-INFO}"

# Wait for database to be ready (with timeout)
echo "⏳ Waiting for database to be ready..."
TIMEOUT=60
ELAPSED=0
until pg_isready -h db -p 5432 -U "${POSTGRES_USER:-defi_user}" > /dev/null 2>&1; do
  if [ $ELAPSED -ge $TIMEOUT ]; then
    echo "❌ Database connection timeout after ${TIMEOUT}s"
    exit 1
  fi
  echo "   Database not ready yet, waiting 2 seconds... (${ELAPSED}s elapsed)"
  sleep 2
  ELAPSED=$((ELAPSED + 2))
done
echo "✅ Database is ready"

# Run database migrations (if Alembic is configured)
echo "📊 Checking for database migrations..."
if [ -f "/app/alembic.ini" ] && [ -d "/app/app/alembic" ]; then
  echo "   Running Alembic migrations..."
  alembic -c /app/alembic.ini upgrade head || echo "⚠️  Migration warnings (may be expected if tables already exist)"
else
  echo "ℹ️  Alembic config or scripts not found, skipping migrations"
  echo "   Tables will be created automatically via SQLAlchemy if needed"
fi

# Verify Python dependencies
echo "🔍 Verifying Python environment..."
python -c "import fastapi, uvicorn, sqlalchemy" || {
  echo "❌ Critical Python dependencies missing!"
  exit 1
}

# Start the application
# Convert LOG_LEVEL to lowercase (uvicorn requires lowercase)
UVICORN_LOG_LEVEL=$(echo "${LOG_LEVEL:-info}" | tr '[:upper:]' '[:lower:]')

echo "🎯 Starting uvicorn server..."
echo "   Host: 0.0.0.0"
echo "   Port: 8000"
echo "   Workers: 1"
echo "   Log Level: ${UVICORN_LOG_LEVEL}"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --log-level "${UVICORN_LOG_LEVEL}"

