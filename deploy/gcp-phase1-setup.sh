#!/bin/bash
# GCP Deployment Script - Phase 1: Account & Project Setup
# Run this script to prepare for GCP deployment

echo "=========================================="
echo "GCP Deployment Preparation"
echo "=========================================="
echo ""

echo "📋 CHECKLIST - Complete these steps manually:"
echo ""
echo "1. 🌐 GCP Account Setup:"
echo "   - Go to: https://console.cloud.google.com"
echo "   - Sign in with Google account"
echo "   - Click 'Get started for free'"
echo "   - Enter credit card (verification only, won't charge)"
echo "   - Select country: India"
echo "   - Verify \$300 credit appears in billing dashboard"
echo ""

echo "2. 🏗️ Create Project:"
echo "   - Click 'Select a project' → 'NEW PROJECT'"
echo "   - Name: defi-risk-assessment"
echo "   - Organization: No organization"
echo "   - Click 'CREATE' → Wait 30 seconds"
echo "   - Select the project from dropdown"
echo ""

echo "3. 🔧 Enable APIs (search bar → click Enable):"
echo "   - Compute Engine API (wait 1 min)"
echo "   - Cloud Storage API (wait 30 sec)"
echo "   - Cloud Scheduler API (wait 30 sec)"
echo "   - Cloud Build API (wait 30 sec)"
echo ""

echo "4. 📊 Verify Billing:"
echo "   - Go to Billing → Overview"
echo "   - Confirm \$300 credit is available"
echo "   - Note your project ID"
echo ""

echo "✅ Once completed, run: ./gcp-phase2-backend.sh"
echo ""
echo "📝 Important Notes:"
echo "   - Keep your project ID handy"
echo "   - Note your GCP account email"
echo "   - Ensure APIs are enabled before proceeding"
echo ""

read -p "Press Enter when you've completed the checklist above..."

echo ""
echo "🎯 Phase 1 Complete! Ready for Phase 2."
echo "Next: Backend VM with LLM setup"




