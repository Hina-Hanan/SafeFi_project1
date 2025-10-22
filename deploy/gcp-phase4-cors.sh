#!/bin/bash
# GCP Deployment Script - Phase 4: CORS Configuration
# This script configures CORS for frontend-backend communication

echo "=========================================="
echo "Phase 4: CORS Configuration"
echo "=========================================="
echo ""

# Get details
read -p "Enter your GCP VM External IP: " VM_IP
read -p "Enter your frontend URL (from Cloud Storage): " FRONTEND_URL

echo ""
echo "🔧 CORS Configuration"
echo "VM IP: $VM_IP"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Create CORS update script for VM
cat > cors_update.sh << EOF
#!/bin/bash
# CORS Update Script - Run this on the VM

echo "🔧 Updating CORS configuration..."

cd ~/main-project/backend
source venv/bin/activate

# Backup original file
cp app/main.py app/main.py.backup

# Update CORS middleware
python3 << 'PYTHON_EOF'
import re

# Read the file
with open('app/main.py', 'r') as f:
    content = f.read()

# Find and replace CORS configuration
cors_pattern = r'allow_origins=\[.*?\]'
new_cors = '''allow_origins=[
        "http://localhost:5173",
        "https://storage.googleapis.com",
        "$FRONTEND_URL",
        "http://$VM_IP:8000"
    ]'''

# Replace the CORS configuration
content = re.sub(cors_pattern, new_cors, content, flags=re.DOTALL)

# Write back
with open('app/main.py', 'w') as f:
    f.write(content)

print("✅ CORS configuration updated")
PYTHON_EOF

# Restart backend service
echo "🔄 Restarting backend service..."
sudo systemctl restart defi-backend

# Wait for service to start
sleep 10

# Test CORS
echo "🧪 Testing CORS configuration..."
curl -H "Origin: $FRONTEND_URL" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:8000/health

echo ""
echo "✅ CORS configuration complete!"
echo "🌐 Frontend: $FRONTEND_URL"
echo "🔗 Backend: http://$VM_IP:8000"
EOF

chmod +x cors_update.sh

echo "📋 INSTRUCTIONS:"
echo ""
echo "1. 🔗 SSH into your VM:"
echo "   - Go to: Compute Engine → VM instances"
echo "   - Find defi-backend-vm → Click SSH"
echo ""

echo "2. 📤 Upload CORS script:"
echo "   - Copy the cors_update.sh content"
echo "   - Create file: nano cors_update.sh"
echo "   - Paste content and save (Ctrl+X, Y, Enter)"
echo "   - Make executable: chmod +x cors_update.sh"
echo ""

echo "3. 🚀 Run CORS update:"
echo "   ./cors_update.sh"
echo ""

echo "4. 🧪 Test the full system:"
echo "   - Open your frontend URL in browser"
echo "   - Check if dashboard loads"
echo "   - Test AI Assistant (should show ONLINE)"
echo "   - Try chatting with AI"
echo ""

echo "5. 🔍 Verify CORS is working:"
echo "   - Open browser developer tools (F12)"
echo "   - Go to Network tab"
echo "   - Refresh the page"
echo "   - Check if API calls to backend succeed"
echo "   - No CORS errors should appear"
echo ""

echo "⏱️ Expected time: 5-10 minutes"
echo "📊 Monitor browser console for any errors"
echo ""
echo "✅ Next: Phase 5 - Automated Updates"

# Create automation setup script for Phase 5
cat > automation_setup.sh << 'EOF'
#!/bin/bash
# Automation Setup Script - Run this on the VM

echo "🔧 Setting up automated updates..."

cd ~/main-project/backend
source venv/bin/activate

# Create update scripts
cat > ~/update_risks.sh << 'RISK_EOF'
#!/bin/bash
cd ~/main-project/backend
source venv/bin/activate
python scripts/auto_update_risks.py >> ~/logs/risk_updates.log 2>&1
echo "$(date): Risk update completed" >> ~/logs/automation.log
RISK_EOF

cat > ~/update_data.sh << 'DATA_EOF'
#!/bin/bash
cd ~/main-project/backend
source venv/bin/activate
python scripts/update_live_data.py >> ~/logs/data_updates.log 2>&1
echo "$(date): Data update completed" >> ~/logs/automation.log
DATA_EOF

# Make scripts executable
chmod +x ~/update_risks.sh ~/update_data.sh

# Create logs directory
mkdir -p ~/logs

# Create admin endpoints
cat > app/api/v1/admin.py << 'ADMIN_EOF'
from fastapi import APIRouter, BackgroundTasks
import subprocess
import logging
import os

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)

@router.post("/trigger-risk-update")
async def trigger_risk_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_script, f"/home/{os.environ.get('USER', 'username')}/update_risks.sh")
    return {"status": "scheduled", "job": "risk_update"}

@router.post("/trigger-data-update")
async def trigger_data_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_script, f"/home/{os.environ.get('USER', 'username')}/update_data.sh")
    return {"status": "scheduled", "job": "data_update"}

def run_script(script_path: str):
    subprocess.run([script_path], shell=False)
ADMIN_EOF

# Add admin router to main router
python3 << 'ROUTER_EOF'
import re

# Read router file
with open('app/api/router.py', 'r') as f:
    content = f.read()

# Add admin import
if 'from app.api.v1 import admin' not in content:
    content = content.replace(
        'from app.api.v1.llm_assistant import router as llm_assistant_router',
        'from app.api.v1.llm_assistant import router as llm_assistant_router\nfrom app.api.v1 import admin'
    )

# Add admin router
if 'api_router.include_router(admin.router)' not in content:
    content = content.replace(
        'api_router.include_router(llm_assistant_router, prefix="/llm", tags=["llm-assistant"])',
        'api_router.include_router(llm_assistant_router, prefix="/llm", tags=["llm-assistant"])\napi_router.include_router(admin.router)'
    )

# Write back
with open('app/api/router.py', 'w') as f:
    f.write(content)

print("✅ Admin endpoints added")
ROUTER_EOF

# Restart backend
sudo systemctl restart defi-backend

echo "✅ Automation setup complete!"
echo "🔗 Admin endpoints available:"
echo "   - POST http://$VM_IP:8000/api/v1/admin/trigger-risk-update"
echo "   - POST http://$VM_IP:8000/api/v1/admin/trigger-data-update"
EOF

chmod +x automation_setup.sh

echo ""
echo "📁 Files created:"
echo "   - cors_update.sh (for CORS configuration)"
echo "   - automation_setup.sh (for Phase 5)"




