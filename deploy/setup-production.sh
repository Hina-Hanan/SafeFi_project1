#!/bin/bash

# Production setup script for SafeFi
set -e

echo "🚀 Setting up SafeFi production environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p ../backend/data/vectorstore
mkdir -p ../backend/logs
mkdir -p ../backend/models

# Set up environment file
if [ ! -f .env.production ]; then
    echo "📝 Creating .env.production file..."
    cat > .env.production << EOF
# Production Environment Configuration

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database Configuration
POSTGRES_USER=defi_user
POSTGRES_PASSWORD=usersafety
POSTGRES_DB=defi_risk_assessment
POSTGRES_PORT=5432

# API Configuration
API_PORT=8000
CORS_ORIGINS=https://safefi.app,https://api.safefi.app

# MLflow Configuration
MLFLOW_PORT=5000

# Frontend Configuration
FRONTEND_PORT=80

# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama

# Email Configuration
EMAIL_ALERTS_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EOF
    echo "⚠️  Please update .env.production with your production values"
fi

# Make scripts executable
chmod +x deploy.sh
chmod +x health-check.sh

echo "✅ Production setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env.production with your configuration"
echo "2. Run './deploy.sh' to deploy the application"
echo "3. Run './health-check.sh' to verify all services"
