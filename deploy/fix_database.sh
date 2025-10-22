#!/bin/bash
# Database Fix Script - Complete Clean and Recreate

echo "🔧 Fixing Database Setup"
echo "========================"

# Switch to postgres user and recreate database
sudo -u postgres psql << 'EOF'
-- Drop and recreate the database completely
DROP DATABASE IF EXISTS defi_risk_assessment;
DROP USER IF EXISTS defi_user;

-- Create fresh user and database
CREATE USER defi_user WITH PASSWORD 'SecurePassword2025!';
CREATE DATABASE defi_risk_assessment OWNER defi_user;
GRANT ALL PRIVILEGES ON DATABASE defi_risk_assessment TO defi_user;

-- Connect to the database and grant schema permissions
\c defi_risk_assessment
GRANT ALL ON SCHEMA public TO defi_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO defi_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO defi_user;

\q
EOF

echo "✅ Database recreated successfully!"
echo ""
echo "Now run from your backend directory:"
echo "  cd ~/SafeFi_project1/backend"
echo "  source venv/bin/activate"
echo "  python -c \"from app.database.models import Base; from app.database.connection import ENGINE; Base.metadata.create_all(ENGINE); print('✅ Tables created!')\""
echo "  python scripts/seed_data.py"





