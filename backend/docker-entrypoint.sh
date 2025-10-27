#!/bin/bash
set -e

echo "🚀 Starting DeFi Risk Assessment Backend..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
until pg_isready -h db -U ${POSTGRES_USER:-defi_user} -d ${POSTGRES_DB:-defi_risk_assessment} 2>/dev/null; do
  echo "   Database not ready yet, waiting 2 seconds..."
  sleep 2
done
echo "✅ Database is ready"

# Run database migrations
echo "📊 Running database migrations..."
alembic upgrade head || echo "⚠️  Migration warnings (may be expected)"

# Start the application
echo "🎯 Starting uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

