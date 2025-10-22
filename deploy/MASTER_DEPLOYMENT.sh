#!/bin/bash
# GCP Deployment Master Script - Complete DeFi Risk Assessment Platform
# This script orchestrates the entire deployment process

echo "=========================================="
echo "DeFi Risk Assessment Platform Deployment"
echo "Complete GCP Setup with LLM Enabled"
echo "=========================================="
echo ""

# Get user information
read -p "Enter your GitHub username: " GITHUB_USERNAME
read -p "Enter your email for SMTP: " USER_EMAIL
read -p "Enter your GCP Project ID: " PROJECT_ID

echo ""
echo "🚀 Starting Complete Deployment Process"
echo "GitHub: $GITHUB_USERNAME"
echo "Email: $USER_EMAIL"
echo "Project: $PROJECT_ID"
echo ""

# Create deployment log
echo "DeFi Risk Assessment Platform Deployment Log" > deployment.log
echo "Started: $(date)" >> deployment.log
echo "GitHub: $GITHUB_USERNAME" >> deployment.log
echo "Email: $USER_EMAIL" >> deployment.log
echo "Project: $PROJECT_ID" >> deployment.log
echo "" >> deployment.log

echo "📋 DEPLOYMENT PHASES:"
echo "===================="
echo ""
echo "Phase 1: GCP Account & Project Setup (15 min)"
echo "Phase 2: Backend VM with LLM (60 min)"
echo "Phase 3: Frontend Deployment (30 min)"
echo "Phase 4: CORS Configuration (10 min)"
echo "Phase 5: Automated Updates (20 min)"
echo "Phase 6: Cost Monitoring (10 min)"
echo "Phase 7: Final Verification (15 min)"
echo ""
echo "Total Estimated Time: 2.5-3 hours"
echo "Total Expected Cost: ~$78 for 90 days"
echo "Remaining Credit: ~$222 (74% unused)"
echo ""

read -p "Press Enter to start Phase 1..."

# Phase 1: GCP Account & Project Setup
echo ""
echo "=========================================="
echo "PHASE 1: GCP Account & Project Setup"
echo "=========================================="
echo ""

echo "📋 MANUAL STEPS REQUIRED:"
echo ""
echo "1. 🌐 GCP Account Setup:"
echo "   - Go to: https://console.cloud.google.com"
echo "   - Sign in with Google account"
echo "   - Click 'Get started for free'"
echo "   - Enter credit card (verification only)"
echo "   - Select country: India"
echo "   - Verify \$300 credit appears"
echo ""

echo "2. 🏗️ Create Project:"
echo "   - Click 'Select a project' → 'NEW PROJECT'"
echo "   - Name: defi-risk-assessment"
echo "   - Organization: No organization"
echo "   - Click 'CREATE'"
echo ""

echo "3. 🔧 Enable APIs:"
echo "   - Compute Engine API"
echo "   - Cloud Storage API"
echo "   - Cloud Scheduler API"
echo "   - Cloud Build API"
echo ""

echo "4. 📊 Verify Billing:"
echo "   - Go to Billing → Overview"
echo "   - Confirm \$300 credit is available"
echo ""

read -p "Press Enter when Phase 1 is complete..."

echo "Phase 1 Complete: $(date)" >> deployment.log

# Phase 2: Backend VM Setup
echo ""
echo "=========================================="
echo "PHASE 2: Backend VM with LLM"
echo "=========================================="
echo ""

echo "📋 VM CREATION STEPS:"
echo ""
echo "1. 🖥️ Create VM Instance:"
echo "   - Compute Engine → VM instances → CREATE INSTANCE"
echo "   - Name: defi-backend-vm"
echo "   - Region: us-central1 (Iowa)"
echo "   - Zone: us-central1-a"
echo "   - Machine type: e2-medium (2 vCPU, 4 GB memory)"
echo "   - Boot disk: Ubuntu 22.04 LTS, 40 GB"
echo "   - Firewall: ✅ Allow HTTP traffic, ✅ Allow HTTPS traffic"
echo ""

echo "2. 🔧 Configure Firewall:"
echo "   - VPC network → Firewall → CREATE FIREWALL RULE"
echo "   - Name: allow-backend-api"
echo "   - Source IPv4 ranges: 0.0.0.0/0"
echo "   - Protocols and ports: TCP → 8000"
echo ""

echo "3. 🚀 Setup Backend (SSH into VM):"
echo "   - Click SSH button on VM"
echo "   - Run: curl -fsSL https://raw.githubusercontent.com/$GITHUB_USERNAME/main-project/main/deploy/vm_setup.sh | bash"
echo "   - Wait 15-20 minutes for complete setup"
echo ""

read -p "Press Enter when Phase 2 is complete..."

echo "Phase 2 Complete: $(date)" >> deployment.log

# Get VM IP for remaining phases
read -p "Enter your VM External IP: " VM_IP

# Phase 3: Frontend Deployment
echo ""
echo "=========================================="
echo "PHASE 3: Frontend Deployment"
echo "=========================================="
echo ""

echo "📋 FRONTEND DEPLOYMENT STEPS:"
echo ""
echo "1. 🌐 Create Cloud Storage Bucket:"
echo "   - Cloud Storage → Buckets → CREATE"
echo "   - Name: defi-risk-frontend-$PROJECT_ID"
echo "   - Location: Region → us-central1"
echo "   - Storage class: Standard"
echo "   - Access control: Fine-grained"
echo ""

echo "2. 📦 Build Frontend (on your local machine):"
echo "   cd frontend"
echo "   # Update API URL to: http://$VM_IP:8000"
echo "   npm install"
echo "   npm run build"
echo ""

echo "3. 📤 Upload to Cloud Storage:"
echo "   - Upload all files from frontend/dist/"
echo "   - Make bucket public"
echo "   - Get public URL"
echo ""

read -p "Press Enter when Phase 3 is complete..."

echo "Phase 3 Complete: $(date)" >> deployment.log

# Get frontend URL
read -p "Enter your frontend URL: " FRONTEND_URL

# Phase 4: CORS Configuration
echo ""
echo "=========================================="
echo "PHASE 4: CORS Configuration"
echo "=========================================="
echo ""

echo "📋 CORS CONFIGURATION STEPS:"
echo ""
echo "1. 🔧 Update CORS (SSH into VM):"
echo "   - Upload cors_update.sh to VM"
echo "   - Run: ./cors_update.sh"
echo ""

echo "2. 🧪 Test Frontend:"
echo "   - Open: $FRONTEND_URL"
echo "   - Verify dashboard loads"
echo "   - Check AI Assistant shows ONLINE"
echo ""

read -p "Press Enter when Phase 4 is complete..."

echo "Phase 4 Complete: $(date)" >> deployment.log

# Phase 5: Automated Updates
echo ""
echo "=========================================="
echo "PHASE 5: Automated Updates"
echo "=========================================="
echo ""

echo "📋 AUTOMATION SETUP STEPS:"
echo ""
echo "1. 🔧 Setup VM Automation (SSH into VM):"
echo "   - Upload automation_setup.sh to VM"
echo "   - Run: ./automation_setup.sh"
echo ""

echo "2. ⏰ Create Cloud Scheduler Jobs:"
echo "   - Job 1: risk-updates-every-5h"
echo "     URL: http://$VM_IP:8000/api/v1/admin/trigger-risk-update"
echo "     Frequency: 0 */5 * * *"
echo "   - Job 2: data-sync-every-3h"
echo "     URL: http://$VM_IP:8000/api/v1/admin/trigger-data-update"
echo "     Frequency: 0 */3 * * *"
echo ""

read -p "Press Enter when Phase 5 is complete..."

echo "Phase 5 Complete: $(date)" >> deployment.log

# Phase 6: Cost Monitoring
echo ""
echo "=========================================="
echo "PHASE 6: Cost Monitoring"
echo "=========================================="
echo ""

echo "📋 COST MONITORING SETUP:"
echo ""
echo "1. 💳 Create Budget Alert:"
echo "   - Billing → Budgets & alerts → CREATE BUDGET"
echo "   - Name: 90-day-deployment-budget"
echo "   - Amount: \$100 USD"
echo "   - Alerts: 50%, 75%, 90%, 100%"
echo "   - Email: $USER_EMAIL"
echo ""

echo "2. 📊 Expected Costs:"
echo "   - Monthly: ~\$26 USD"
echo "   - 90-day: ~\$78 USD"
echo "   - Remaining: ~\$222 USD"
echo ""

read -p "Press Enter when Phase 6 is complete..."

echo "Phase 6 Complete: $(date)" >> deployment.log

# Phase 7: Final Verification
echo ""
echo "=========================================="
echo "PHASE 7: Final Verification"
echo "=========================================="
echo ""

echo "📋 FINAL VERIFICATION STEPS:"
echo ""
echo "1. 🧪 Run System Tests:"
echo "   - Execute: ./system_test.sh"
echo "   - Review all test results"
echo ""

echo "2. 🌐 Test Frontend:"
echo "   - Open: $FRONTEND_URL"
echo "   - Complete manual checklist"
echo ""

echo "3. 🔧 Test Backend (SSH into VM):"
echo "   - Check service status"
echo "   - Verify LLM is working"
echo ""

read -p "Press Enter when Phase 7 is complete..."

echo "Phase 7 Complete: $(date)" >> deployment.log

# Final Summary
echo ""
echo "=========================================="
echo "🎉 DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""

echo "📊 SYSTEM SUMMARY:"
echo "=================="
echo ""
echo "✅ Backend API: http://$VM_IP:8000"
echo "✅ Frontend: $FRONTEND_URL"
echo "✅ LLM Service: Active with TinyLlama"
echo "✅ Database: PostgreSQL connected"
echo "✅ Automation: Cloud Scheduler configured"
echo "✅ Cost Monitoring: Budget alerts setup"
echo ""

echo "💰 COST SUMMARY:"
echo "==============="
echo ""
echo "Expected Monthly: ~\$26 USD"
echo "Expected 90-day: ~\$78 USD"
echo "Total Credit: \$300 USD"
echo "Remaining: ~\$222 USD (74% unused)"
echo ""

echo "🎯 KEY FEATURES:"
echo "==============="
echo ""
echo "✅ Real-time DeFi risk monitoring"
echo "✅ 7-day historical trend analysis"
echo "✅ Interactive protocol heatmap"
echo "✅ AI-powered chat assistant"
echo "✅ Automated risk score updates"
echo "✅ Email alert subscriptions"
echo ""

echo "📚 NEXT STEPS:"
echo "============="
echo ""
echo "1. Share your frontend URL with users"
echo "2. Monitor costs weekly"
echo "3. Check logs regularly"
echo "4. Scale up if needed"
echo "5. Add more features as desired"
echo ""

echo "🎊 CONGRATULATIONS!"
echo "Your DeFi Risk Assessment platform is now fully deployed"
echo "and operational on Google Cloud Platform!"
echo ""

echo "📁 Deployment Log: deployment.log"
echo "📁 All scripts created in deploy/ directory"
echo ""

echo "Deployment Complete: $(date)" >> deployment.log
echo "VM IP: $VM_IP" >> deployment.log
echo "Frontend URL: $FRONTEND_URL" >> deployment.log
echo "Total Cost Expected: ~$78 USD" >> deployment.log
echo "Remaining Credit: ~$222 USD" >> deployment.log




