#!/bin/bash
# Simple Database Fix Script - Run as postgres user

echo "🔧 Fixing Database Setup"
echo "========================"

# Drop and recreate database (run as postgres user)
psql << 'EOF'
-- Drop and recreate the database completely
DROP DATABASE IF EXISTS defi_risk_assessment;
DROP USER IF EXISTS defi_user;

-- Create fresh user and database
CREATE USER defi_user WITH PASSWORD 'SecurePassword2025!';
CREATE DATABASE defi_risk_assessment OWNER defi_user;
GRANT ALL PRIVILEGES ON DATABASE defi_risk_assessment TO defi_user;

\q
EOF

# Grant schema permissions
psql -d defi_risk_assessment << 'EOF'
GRANT ALL ON SCHEMA public TO defi_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO defi_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO defi_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO defi_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO defi_user;
\q
EOF

echo "✅ Database recreated successfully!"
echo ""
echo "Now creating tables..."
cd ~/SafeFi_project1/backend
source venv/bin/activate
export PYTHONPATH=$PWD:$PYTHONPATH
python -c "from app.database.models import Base; from app.database.connection import ENGINE; Base.metadata.create_all(ENGINE); print('✅ Tables created!')"

echo ""
echo "Verifying tables..."
psql -U defi_user -d defi_risk_assessment << 'EOF'
\dt
\q
EOF

echo ""
echo "✅ Setup complete! Now you can run:"
echo "   python scripts/seed_data.py"





