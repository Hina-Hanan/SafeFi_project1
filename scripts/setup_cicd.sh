#!/bin/bash
# Quick CI/CD Setup Script
# Run this to set up SSH keys and verify GitHub Actions configuration

set -e

echo "🚀 Setting up CI/CD for SafeFi Project"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Generate SSH key for GitHub Actions
echo "📝 Step 1: Generating SSH key for GitHub Actions..."
if [ ! -f ~/.ssh/github_actions_deploy ]; then
    ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy -N ""
    echo "✅ SSH key generated: ~/.ssh/github_actions_deploy"
else
    echo "⚠️  SSH key already exists: ~/.ssh/github_actions_deploy"
fi

echo ""
echo "📋 Step 2: Copy these to GitHub Secrets:"
echo "========================================"
echo ""
echo "1. GCP_VM_SSH_KEY (Private Key):"
echo "   Path: ~/.ssh/github_actions_deploy"
echo "   Content:"
cat ~/.ssh/github_actions_deploy
echo ""
echo "2. Public Key (add to VM):"
echo "   Path: ~/.ssh/github_actions_deploy.pub"
echo "   Content:"
cat ~/.ssh/github_actions_deploy.pub
echo ""
echo "📋 Step 3: Required GitHub Secrets:"
echo "========================================"
echo ""
echo "Required Secrets (add in GitHub → Settings → Secrets):"
echo ""
echo "Backend Deployment:"
echo "  - GCP_VM_IP: Your VM's IP address"
echo "  - GCP_VM_SSH_KEY: (Private key shown above)"
echo ""
echo "Frontend Deployment:"
echo "  - GCP_PROJECT_ID: Your GCP project ID"
echo "  - GCS_BUCKET_NAME: Your GCS bucket name"
echo "  - GCP_SA_KEY: Service Account JSON key"
echo "  - VITE_API_BASE_URL: (Optional) Your API URL"
echo "  - GCS_CUSTOM_DOMAIN: (Optional) Custom domain"
echo ""
echo "📋 Step 4: Add public key to VM"
echo "========================================"
echo ""
echo "Run this command (replace YOUR_VM_IP):"
echo "  ssh-copy-id -i ~/.ssh/github_actions_deploy.pub hinahanan2003@YOUR_VM_IP"
echo ""
echo "Or manually add to VM:"
echo "  ssh hinahanan2003@YOUR_VM_IP"
echo "  mkdir -p ~/.ssh"
echo "  echo '$(cat ~/.ssh/github_actions_deploy.pub)' >> ~/.ssh/authorized_keys"
echo "  chmod 600 ~/.ssh/authorized_keys"
echo ""
echo "✅ Setup script completed!"
echo ""
echo "Next steps:"
echo "  1. Add secrets to GitHub repository"
echo "  2. Add public key to VM"
echo "  3. Create a test PR to verify CI works"
echo "  4. Merge to main to trigger deployment"




