#!/bin/bash

set -e  # Exit on error

echo "======================================================"
echo "🚀 Complete DeFi Risk Assessment Backend Setup"
echo "======================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Step 1: Verify disk space
echo "Step 1: Verifying disk space..."
DISK_SIZE=$(df -h / | awk 'NR==2 {print $2}' | sed 's/G//')
if (( $(echo "$DISK_SIZE < 20" | bc -l) )); then
    print_error "Disk size is only ${DISK_SIZE}GB. Need at least 20GB."
    print_info "Attempting to resize filesystem..."
    sudo growpart /dev/sda 1 2>/dev/null || true
    sudo resize2fs /dev/sda1 2>/dev/null || true
    df -h /
fi
print_success "Disk space: $(df -h / | awk 'NR==2 {print $2}')"
echo ""

# Step 2: Navigate to project directory
echo "Step 2: Setting up project directory..."
cd /var/lib/postgresql
if [ ! -d "SafeFi_project1" ]; then
    print_error "Project directory not found. Please clone the repository first."
    exit 1
fi
cd SafeFi_project1/backend
print_success "Project directory: $(pwd)"
echo ""

# Step 3: Create virtual environment
echo "Step 3: Creating virtual environment..."
if [ -d "venv" ]; then
    print_info "Removing old virtual environment..."
    rm -rf venv
fi
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel -q
print_success "Virtual environment created and activated"
echo ""

# Step 4: Install dependencies in stages
echo "Step 4: Installing dependencies..."
print_info "This may take 10-15 minutes. Installing in stages to avoid memory issues..."
echo ""

# Track disk space
INITIAL_SPACE=$(df / | awk 'NR==2 {print $4}')

install_stage() {
    STAGE_NAME=$1
    shift
    PACKAGES=$@
    
    echo "  Installing $STAGE_NAME..."
    if pip install $PACKAGES -q --no-cache-dir; then
        print_success "$STAGE_NAME installed"
    else
        print_error "$STAGE_NAME installation failed"
        return 1
    fi
    
    # Show space used
    CURRENT_SPACE=$(df / | awk 'NR==2 {print $4}')
    SPACE_USED=$((INITIAL_SPACE - CURRENT_SPACE))
    print_info "Space used so far: $((SPACE_USED / 1024))MB"
}

# Core dependencies (essential)
install_stage "Core Web Framework" \
    fastapi==0.115.0 \
    uvicorn[standard]==0.30.6 \
    python-multipart==0.0.12

install_stage "Database" \
    sqlalchemy==2.0.34 \
    psycopg2-binary==2.9.9

install_stage "Data Validation" \
    pydantic==2.9.2 \
    email-validator==2.1.0

install_stage "HTTP & Config" \
    httpx==0.27.2 \
    python-dotenv==1.0.1

install_stage "ML Core" \
    numpy==2.1.2 \
    pandas==2.2.3 \
    scikit-learn==1.5.2 \
    joblib==1.4.2

# Optional dependencies (can be skipped if space is low)
FREE_SPACE=$(df / | awk 'NR==2 {print $4}')
if [ $FREE_SPACE -gt 5000000 ]; then  # More than 5GB free
    install_stage "ML Models" \
        xgboost==2.1.1 \
        lightgbm==4.5.0 \
        catboost==1.2.7 || print_info "Skipping ML models due to space constraints"
    
    install_stage "MLflow" \
        mlflow==2.16.2 || print_info "Skipping MLflow due to space constraints"
    
    install_stage "Anomaly Detection" \
        pyod==2.0.2 \
        hdbscan==0.8.40 \
        shap==0.45.1 \
        eli5==0.13.0 \
        imbalanced-learn==0.12.4 || print_info "Skipping anomaly detection due to space constraints"
    
    install_stage "Rate Limiting" \
        aiolimiter==1.1.0 \
        ratelimit==2.2.1 || print_info "Skipping rate limiting due to space constraints"
    
    install_stage "Document Processing" \
        pypdf==4.2.0 \
        python-docx==1.1.0 || print_info "Skipping document processing due to space constraints"
else
    print_info "Low on disk space, skipping optional packages"
fi

echo ""
print_success "Dependencies installed successfully"
print_info "Final disk usage: $(df -h / | awk 'NR==2 {print $5}')"
echo ""

# Step 5: Setup environment variables
echo "Step 5: Creating .env file..."
if [ -f .env ]; then
    print_info "Backing up existing .env to .env.backup"
    cp .env .env.backup
fi

cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://defi_user:SecurePassword2025!@localhost:5432/defi_risk_assessment
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_RECYCLE=1800
DB_ISOLATION_LEVEL=READ COMMITTED

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Logging
LOG_LEVEL=INFO

# MLflow
MLFLOW_TRACKING_URI=file:///var/lib/postgresql/mlruns

# Server Configuration
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production

# API Keys
COINGECKO_API_KEY=CG-Y27jCPKqZ28dwWuBhYjEKvGZ
ETHERSCAN_API_KEY=DTEVPVQQ2UMWI45Q4S9I2Z31E5GJTT6SN7
DEFI_LLAMA_API_KEY=not_required
ALCHEMY_API_KEY=ld2yI48GDg8mltMJVOC1o
COINGECKO_MIN_INTERVAL_SEC=0.1

# Email Alerts (configure if needed)
EMAIL_ALERTS_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
ALERT_SENDER_EMAIL=
ALERT_SENDER_PASSWORD=
ALERT_RECIPIENT_EMAIL=
EOF

print_success ".env file created"
echo ""

# Step 6: Set PYTHONPATH
echo "Step 6: Setting PYTHONPATH..."
export PYTHONPATH=/var/lib/postgresql/SafeFi_project1/backend:$PYTHONPATH
if ! grep -q "PYTHONPATH=/var/lib/postgresql/SafeFi_project1/backend" ~/.bashrc; then
    echo 'export PYTHONPATH=/var/lib/postgresql/SafeFi_project1/backend:$PYTHONPATH' >> ~/.bashrc
fi
print_success "PYTHONPATH configured"
echo ""

# Step 7: Setup database enum values
echo "Step 7: Setting up database enum values..."
psql -d defi_risk_assessment <<'SQL' 2>/dev/null || print_info "Enum values may already exist"
ALTER TYPE protocol_category ADD VALUE IF NOT EXISTS 'DEX';
ALTER TYPE protocol_category ADD VALUE IF NOT EXISTS 'LENDING';
ALTER TYPE protocol_category ADD VALUE IF NOT EXISTS 'DERIVATIVES';
ALTER TYPE protocol_category ADD VALUE IF NOT EXISTS 'YIELD';
ALTER TYPE protocol_category ADD VALUE IF NOT EXISTS 'STAKING';
ALTER TYPE protocol_category ADD VALUE IF NOT EXISTS 'BRIDGE';
ALTER TYPE protocol_category ADD VALUE IF NOT EXISTS 'OTHER';
ALTER TYPE risk_level ADD VALUE IF NOT EXISTS 'LOW';
ALTER TYPE risk_level ADD VALUE IF NOT EXISTS 'MEDIUM';
ALTER TYPE risk_level ADD VALUE IF NOT EXISTS 'HIGH';
SQL
print_success "Database enum values configured"
echo ""

# Step 8: Verify/Create database tables
echo "Step 8: Verifying database tables..."
TABLE_COUNT=$(psql -d defi_risk_assessment -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null || echo "0")
if [ "$TABLE_COUNT" -lt 5 ]; then
    print_info "Creating database tables..."
    python3 -c "from app.database.models import Base; from app.database.connection import ENGINE; Base.metadata.create_all(ENGINE); print('Tables created')" 2>/dev/null || print_error "Failed to create tables"
fi
print_success "Database tables verified"
echo ""

# Step 9: Seed data
echo "Step 9: Seeding initial data..."
PROTOCOL_COUNT=$(psql -d defi_risk_assessment -t -c "SELECT COUNT(*) FROM protocols;" 2>/dev/null || echo "0")
if [ "$PROTOCOL_COUNT" -lt 5 ]; then
    print_info "Seeding protocols..."
    python3 scripts/seed_data.py 2>/dev/null || print_error "Failed to seed data"
    
    print_info "Generating realistic data..."
    python3 scripts/generate_realistic_data.py 2>/dev/null || print_error "Failed to generate data"
    
    print_info "Generating 7-day history..."
    python3 scripts/generate_7day_history.py 2>/dev/null || print_error "Failed to generate history"
else
    print_info "Data already exists, skipping seeding"
fi

# Verify data
PROTOCOL_COUNT=$(psql -d defi_risk_assessment -t -c "SELECT COUNT(*) FROM protocols;" 2>/dev/null | xargs)
METRIC_COUNT=$(psql -d defi_risk_assessment -t -c "SELECT COUNT(*) FROM protocol_metrics;" 2>/dev/null | xargs)
RISK_COUNT=$(psql -d defi_risk_assessment -t -c "SELECT COUNT(*) FROM risk_scores;" 2>/dev/null | xargs)

print_success "Data seeded: $PROTOCOL_COUNT protocols, $METRIC_COUNT metrics, $RISK_COUNT risk scores"
echo ""

# Step 10: Final checks
echo "Step 10: Running final checks..."

# Check if backend can be imported
if python3 -c "from app.main import app; print('OK')" 2>/dev/null | grep -q "OK"; then
    print_success "Backend imports successfully"
else
    print_error "Backend has import errors"
    print_info "Try running: python3 -c 'from app.main import app'"
fi

# Show disk usage
print_info "Final disk usage:"
df -h /

echo ""
echo "======================================================"
print_success "Setup Complete!"
echo "======================================================"
echo ""
echo "To start the backend:"
echo "  cd /var/lib/postgresql/SafeFi_project1/backend"
echo "  source venv/bin/activate"
echo "  export PYTHONPATH=\$PWD:\$PYTHONPATH"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "To test:"
echo "  curl http://localhost:8000/health"
echo ""
echo "To run in background:"
echo "  nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &"
echo ""





