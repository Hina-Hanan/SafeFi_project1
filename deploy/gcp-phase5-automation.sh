#!/bin/bash
# GCP Deployment Script - Phase 5: Automated Updates
# This script sets up Cloud Scheduler for automated updates

echo "=========================================="
echo "Phase 5: Automated Updates"
echo "=========================================="
echo ""

# Get details
read -p "Enter your GCP VM External IP: " VM_IP
read -p "Enter your GCP Project ID: " PROJECT_ID

echo ""
echo "⏰ Automated Updates Setup"
echo "VM IP: $VM_IP"
echo "Project: $PROJECT_ID"
echo ""

echo "📋 INSTRUCTIONS:"
echo ""
echo "1. 🔧 Setup VM Automation (SSH into VM):"
echo "   - Upload automation_setup.sh to VM"
echo "   - Run: ./automation_setup.sh"
echo "   - This creates admin endpoints for triggering updates"
echo ""

echo "2. ⏰ Create Cloud Scheduler Jobs:"
echo ""
echo "   Job 1 - Risk Updates (every 5 hours):"
echo "   - Go to: Cloud Scheduler → CREATE JOB"
echo "   - Name: risk-updates-every-5h"
echo "   - Region: us-central1"
echo "   - Frequency: 0 */5 * * *"
echo "   - Timezone: Asia/Kolkata (IST)"
echo "   - Target: HTTP"
echo "   - URL: http://$VM_IP:8000/api/v1/admin/trigger-risk-update"
echo "   - HTTP method: POST"
echo "   - Click CREATE"
echo ""

echo "   Job 2 - Data Updates (every 3 hours):"
echo "   - Go to: Cloud Scheduler → CREATE JOB"
echo "   - Name: data-sync-every-3h"
echo "   - Region: us-central1"
echo "   - Frequency: 0 */3 * * *"
echo "   - Timezone: Asia/Kolkata (IST)"
echo "   - Target: HTTP"
echo "   - URL: http://$VM_IP:8000/api/v1/admin/trigger-data-update"
echo "   - HTTP method: POST"
echo "   - Click CREATE"
echo ""

echo "3. 🧪 Test Automation:"
echo "   - Go to Cloud Scheduler"
echo "   - Click on each job → RUN NOW"
echo "   - Check VM logs: tail -f ~/logs/automation.log"
echo "   - Verify updates are working"
echo ""

echo "4. 📊 Monitor Automation:"
echo "   - Check logs: tail -f ~/logs/risk_updates.log"
echo "   - Check logs: tail -f ~/logs/data_updates.log"
echo "   - Verify data is updating in frontend"
echo ""

echo "⏱️ Expected time: 15-20 minutes"
echo "📊 Monitor Cloud Scheduler dashboard"
echo ""
echo "✅ Next: Phase 6 - Cost Monitoring"

# Create cost monitoring script
cat > cost_monitoring.sh << 'EOF'
#!/bin/bash
# Cost Monitoring Script

echo "💰 GCP Cost Monitoring Setup"
echo "=============================="
echo ""

echo "📋 COST MONITORING CHECKLIST:"
echo ""
echo "1. 💳 Budget Alerts:"
echo "   - Go to: Billing → Budgets & alerts → CREATE BUDGET"
echo "   - Name: 90-day-deployment-budget"
echo "   - Amount: $100 USD"
echo "   - Alerts: 50%, 75%, 90%, 100%"
echo "   - Email: your-email@gmail.com"
echo "   - Click CREATE"
echo ""

echo "2. 📊 Weekly Monitoring:"
echo "   - Check: Billing → Reports"
echo "   - Expected costs:"
echo "     • Week 1-4: ~$24-26/month"
echo "     • Total 90 days: ~$75-80"
echo "     • Remaining: ~$220"
echo ""

echo "3. 🔍 Cost Breakdown:"
echo "   - Compute Engine e2-medium: ~$24/month"
echo "   - Cloud Storage: ~$0.50/month"
echo "   - Cloud Scheduler: ~$0.30/month"
echo "   - Egress (data transfer): ~$1/month"
echo "   - Total: ~$26/month"
echo ""

echo "4. ⚠️ Cost Optimization Tips:"
echo "   - Monitor VM usage patterns"
echo "   - Consider stopping VM during low usage"
echo "   - Use Cloud Scheduler to start/stop VM if needed"
echo "   - Check for unused resources weekly"
echo ""

echo "5. 📈 Scaling Options (if needed):"
echo "   - Upgrade to e2-standard-2: +$25/month (better performance)"
echo "   - Add more storage: +$2/month per 10GB"
echo "   - Add Cloud CDN: +$5/month (faster frontend)"
echo ""

echo "✅ Cost monitoring setup complete!"
echo "💡 Remember: You have $300 credit for 90 days"
echo "🎯 Target: Stay under $100 total usage"
EOF

chmod +x cost_monitoring.sh

echo ""
echo "📁 Files created:"
echo "   - automation_setup.sh (for VM automation)"
echo "   - cost_monitoring.sh (for Phase 6)"




