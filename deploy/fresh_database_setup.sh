#!/bin/bash

echo "🔥 COMPLETE DATABASE RESET - Starting Fresh"
echo "=============================================="

# Set environment
export PYTHONPATH=/var/lib/postgresql/SafeFi_project1/backend:$PYTHONPATH
cd /var/lib/postgresql/SafeFi_project1/backend

echo "📋 Step 1: Drop ALL existing database objects"
psql -d defi_risk_assessment << 'EOF'
-- Drop all tables and related objects
DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS risk_scores CASCADE;
DROP TABLE IF EXISTS protocol_metrics CASCADE;
DROP TABLE IF EXISTS email_subscribers CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS protocols CASCADE;

-- Drop custom types
DROP TYPE IF EXISTS protocol_category CASCADE;
DROP TYPE IF EXISTS risk_level CASCADE;

-- Drop any remaining sequences
DROP SEQUENCE IF EXISTS protocols_id_seq CASCADE;
DROP SEQUENCE IF EXISTS protocol_metrics_id_seq CASCADE;
DROP SEQUENCE IF EXISTS risk_scores_id_seq CASCADE;
DROP SEQUENCE IF EXISTS users_id_seq CASCADE;
DROP SEQUENCE IF EXISTS alerts_id_seq CASCADE;
DROP SEQUENCE IF EXISTS email_subscribers_id_seq CASCADE;

SELECT 'All objects dropped!' as status;
\q
EOF

echo "📋 Step 2: Create database tables using SQLAlchemy models"
python3 -c "
import sys
sys.path.append('/var/lib/postgresql/SafeFi_project1/backend')

from app.database.models import Base
from app.database.connection import ENGINE
from sqlalchemy import text

print('Creating all tables from models...')

# Create all tables
Base.metadata.create_all(ENGINE, checkfirst=False)
print('✅ All tables created successfully!')

# Verify tables exist
with ENGINE.connect() as conn:
    result = conn.execute(text(\"SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename\"))
    tables = [row[0] for row in result]
    print(f'📊 Created tables: {tables}')
    
    # Check table structures
    for table in tables:
        result = conn.execute(text(f\"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{table}' ORDER BY ordinal_position\"))
        columns = [(row[0], row[1]) for row in result]
        print(f'  {table}: {[col[0] for col in columns]}')
"

echo "📋 Step 3: Seed initial data"
python3 scripts/seed_data.py

echo "📋 Step 4: Verify data was inserted"
psql -d defi_risk_assessment << 'EOF'
SELECT 'protocols' as table_name, COUNT(*) as count FROM protocols
UNION ALL
SELECT 'protocol_metrics', COUNT(*) FROM protocol_metrics
UNION ALL
SELECT 'risk_scores', COUNT(*) FROM risk_scores
UNION ALL
SELECT 'email_subscribers', COUNT(*) FROM email_subscribers;
\q
EOF

echo "🎉 DATABASE SETUP COMPLETE!"
echo "=========================="
echo "✅ All tables created"
echo "✅ Initial data seeded"
echo "✅ Ready for deployment!"




