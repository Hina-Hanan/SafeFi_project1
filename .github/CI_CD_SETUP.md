# CI/CD Setup Guide

This guide explains how to set up CI/CD for your SafeFi project using GitHub Actions.

## 📋 Prerequisites

1. **GitHub Repository**: Your code should be in a GitHub repository
2. **GCP VM**: Backend deployed on GCP VM
3. **GCS Bucket**: Frontend deployed to Google Cloud Storage
4. **SSH Access**: SSH key pair for VM access
5. **GCP Service Account**: For GCS deployment
6. **Ollama Service**: LLM service running on VM host (required for LLM features)

## 🔐 Required GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

### Backend Deployment Secrets

1. **`GCP_VM_IP`** (Required)
   - Your GCP VM's external IP address
   - Example: `34.55.12.211`

2. **`GCP_VM_SSH_KEY`** (Required)
   - Your private SSH key for VM access
   - Generate with: `ssh-keygen -t ed25519 -C "github-actions"`
   - Copy the **private** key content (including `-----BEGIN OPENSSH PRIVATE KEY-----`)

3. **`GCP_VM_USER`** (Optional)
   - SSH username for VM access
   - Default: `hinahanan2003`
   - Only set this secret if your VM uses a different username

4. **`GCP_PROJECT_PATH`** (Optional)
   - Path on VM where the project is deployed
   - Default: `/var/lib/postgresql/SafeFi_project1`
   - Only set this secret if your project is in a different location

### Frontend Deployment Secrets

3. **`GCP_PROJECT_ID`**
   - Your GCP project ID
   - Example: `my-project-123456`

4. **`GCS_BUCKET_NAME`**
   - Your GCS bucket name for frontend
   - Example: `safefi-frontend`

5. **`GCP_SA_KEY`**
   - Service Account JSON key with Storage Admin role
   - Create in GCP Console → IAM & Admin → Service Accounts
   - Role: Storage Admin
   - Download JSON key and paste entire content

6. **`VITE_API_BASE_URL`** (Optional)
   - Your API base URL for frontend
   - Example: `https://api.safefi.live` or `http://YOUR_VM_IP:8000`

7. **`GCS_CUSTOM_DOMAIN`** (Optional)
   - Custom domain for frontend
   - Example: `https://safefi.live`

## 🔑 Setting Up SSH Access

### Step 1: Generate SSH Key Pair

```bash
# Generate new SSH key pair (if you don't have one)
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy

# This creates:
# ~/.ssh/github_actions_deploy (private key - add to GitHub Secrets)
# ~/.ssh/github_actions_deploy.pub (public key - add to VM)
```

### Step 2: Add Public Key to VM

```bash
# Copy public key to VM
ssh-copy-id -i ~/.ssh/github_actions_deploy.pub hinahanan2003@YOUR_VM_IP

# Or manually add to VM:
ssh hinahanan2003@YOUR_VM_IP
mkdir -p ~/.ssh
echo "YOUR_PUBLIC_KEY_CONTENT" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Step 3: Add Private Key to GitHub Secrets

```bash
# Copy private key content
cat ~/.ssh/github_actions_deploy

# Add entire content (including BEGIN/END lines) to GitHub Secret: GCP_VM_SSH_KEY
```

## 🔧 Setting Up GCP Service Account

### Step 1: Create Service Account

1. Go to GCP Console → IAM & Admin → Service Accounts
2. Click "Create Service Account"
3. Name: `github-actions-frontend`
4. Description: "For GitHub Actions frontend deployment"
5. Click "Create and Continue"

### Step 2: Grant Permissions

1. Role: **Storage Admin** (for GCS bucket access)
2. Click "Continue" → "Done"

### Step 3: Create and Download Key

1. Click on the service account
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose "JSON"
5. Download the JSON file
6. Copy entire content to GitHub Secret: `GCP_SA_KEY`

## 📝 Setting Up GCS Bucket

If you haven't created a bucket yet:

```bash
# Authenticate
gcloud auth login

# Create bucket
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://safefi-frontend/

# Make bucket public
gsutil iam ch allUsers:objectViewer gs://safefi-frontend/

# Set website configuration (optional)
gsutil web set -m index.html -e index.html gs://safefi-frontend/
```

## 🚀 Testing CI/CD

### Test CI (Pull Request)

1. Create a new branch
2. Make a small change
3. Push and create PR
4. CI will run automatically
5. Check Actions tab for results

### Test CD (Deploy)

1. Merge PR to `main` branch
2. CD workflows will trigger automatically
3. Monitor deployment in Actions tab
4. Verify deployment:
   ```bash
   # Check backend
   curl http://YOUR_VM_IP:8000/health
   
   # Check frontend
   curl https://storage.googleapis.com/YOUR_BUCKET/index.html
   ```

## 🔄 Manual Deployment

You can also trigger deployments manually (bypasses CI check - use with caution):

1. Go to Actions tab
2. Select either:
   - "CD - Deploy Backend to GCP VM"
   - "CD - Deploy Frontend to GCS"
3. Click "Run workflow"
4. Choose branch (usually `main`)
5. Click "Run workflow"

**Note**: Manual deployment bypasses the CI check. Only use this for:
- Emergency deployments
- Hotfixes that need immediate deployment
- Testing deployment process
- Situations where CI passed but CD didn't trigger automatically

For normal deployments, let the workflow run automatically after CI passes.

## 🤖 Setting Up Ollama Service

The backend deployment requires Ollama to be running on the VM host for LLM features.

### Step 1: Install Ollama

```bash
# On your GCP VM
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 2: Start Ollama Service

```bash
# Start Ollama on all interfaces (required for Docker access)
OLLAMA_HOST=0.0.0.0:11434 nohup ollama serve > /tmp/ollama.log 2>&1 &

# Or add to systemd for auto-start:
sudo systemctl enable ollama
sudo systemctl start ollama
```

### Step 3: Pull Required Model

```bash
# Pull the tinyllama model (or your preferred model)
ollama pull tinyllama

# Verify model is available
ollama list
```

### Step 4: Verify Ollama is Running

```bash
# Check if Ollama is listening on port 11434
ss -tlnp | grep 11434

# Test Ollama API
curl http://localhost:11434/api/tags
```

The CI/CD pipeline will automatically verify Ollama before deployment.

## 📜 Post-Deployment Scripts

The backend deployment automatically runs the following scripts in order:

1. **`seed_real_protocols.py`**
   - Seeds real DeFi protocols into the database
   - Skips if protocols already exist (idempotent)
   - Runs on every deployment

2. **`real_data.py`**
   - Initializes/updates protocol data with market metrics
   - Calculates initial risk scores
   - Generates realistic market data

3. **`auto_update_risks.py`**
   - Performs automated risk assessment
   - Updates risk scores for all protocols
   - Analyzes market conditions

4. **`7historical_graph.py`**
   - Generates 7-day historical data for charts
   - Creates historical risk score snapshots
   - Required for dashboard visualizations

5. **`initialize_vector_store.py`**
   - Initializes vector store for LLM/RAG features
   - Only runs if `RAG_ENABLED=true`
   - Required for AI assistant functionality

### Script Execution Details

- Each script has a **5-minute timeout**
- Scripts run **sequentially** (one after another)
- Database state is **verified after each script**
- **Rollback is triggered** if any script fails
- Script outputs are **logged for debugging**

## 📊 Workflow Overview

### CI Pipeline (on PR)
- ✅ Runs backend tests with PostgreSQL
- ✅ Tests frontend (lint, type-check, build)
- ✅ Builds Docker images (slim and full LLM)
- ✅ Verifies LLM dependencies in full build
- ✅ Does NOT deploy

### CD Backend Pipeline (after CI passes)
- ✅ **Triggers**: Only runs after CI workflow completes successfully
- ✅ **File Change Detection**: Automatically checks if backend files changed
- ✅ **Pre-deployment checks**:
  - Disk space verification (min 5GB)
  - Ollama service verification
  - Ollama API accessibility check
  - tinyllama model availability
- ✅ **Deployment**:
  - Copies files to VM
  - Builds Docker image with LLM support
  - Starts containers (always uses LLM build)
  - Waits for API health check
- ✅ **Post-deployment scripts**:
  - Runs all scripts in order
  - Verifies database state after each
- ✅ **Final verification**:
  - API health check
  - LLM service availability
  - Vector store initialization
- ✅ **Rollback on failure**:
  - Automatically stops containers on error
  - Provides logs for debugging
- ✅ **Manual override**: Can be triggered manually via `workflow_dispatch` (bypasses CI)

### CD Frontend Pipeline (after CI passes)
- ✅ **Triggers**: Only runs after CI workflow completes successfully
- ✅ **File Change Detection**: Automatically checks if frontend files changed
- ✅ Builds frontend with environment variables
- ✅ Verifies build output
- ✅ Uploads to GCS bucket
- ✅ Sets correct content types
- ✅ Verifies deployment accessibility
- ✅ Provides deployment summary
- ✅ **Manual override**: Can be triggered manually via `workflow_dispatch` (bypasses CI)

## 🔄 Rollback Procedures

### Automatic Rollback

The deployment workflow automatically triggers rollback on:
- ❌ Pre-deployment check failures (disk space, Ollama)
- ❌ Docker build failures
- ❌ Container startup failures
- ❌ API health check failures
- ❌ Post-deployment script failures
- ❌ Database verification failures

On rollback:
- Containers are stopped automatically
- Previous state is preserved in backup files
- Logs are available for debugging

### Manual Rollback

If automatic rollback doesn't work:

```bash
# SSH into VM
ssh hinahanan2003@YOUR_VM_IP

# Stop containers
cd /var/lib/postgresql/SafeFi_project1
docker compose -f docker-compose.yml -f docker-compose.llm.yml down

# Check backup logs
cat /tmp/docker_backup_status.txt
cat /tmp/docker_backup_logs.txt

# Restore from previous Git commit if needed
git log --oneline -10
git checkout <previous-commit-hash>
docker compose -f docker-compose.yml -f docker-compose.llm.yml up -d
```

## 🛠️ Troubleshooting

### SSH Connection Issues

```bash
# Test SSH connection manually
ssh -i ~/.ssh/github_actions_deploy hinahanan2003@YOUR_VM_IP

# If fails, check:
# 1. Public key is in ~/.ssh/authorized_keys on VM
# 2. Permissions: chmod 600 ~/.ssh/authorized_keys
# 3. SSH service is running: sudo systemctl status ssh
```

### Ollama Service Issues

```bash
# Check if Ollama is running
ss -tlnp | grep 11434
ps aux | grep ollama

# Check Ollama logs
cat /tmp/ollama.log

# Restart Ollama
sudo pkill -f ollama
OLLAMA_HOST=0.0.0.0:11434 nohup ollama serve > /tmp/ollama.log 2>&1 &

# Verify API
curl http://localhost:11434/api/tags

# Check if model is available
ollama list
```

### Permission Issues

The workflow automatically handles permission issues, but if you encounter problems:

```bash
# If git pull fails due to permissions:
# Option 1: Fix directory ownership
sudo chown -R hinahanan2003:hinahanan2003 /var/lib/postgresql/SafeFi_project1

# Option 2: Add user to docker group (if docker commands fail)
sudo usermod -aG docker hinahanan2003
# Then logout and login again

# Option 3: Check if postgres user owns the directory
ls -la /var/lib/postgresql/SafeFi_project1

# If postgres user owns it, ensure hinahanan2003 has sudo access
sudo visudo
# Add: hinahanan2003 ALL=(postgres) NOPASSWD: /usr/bin/git

# For Docker permission issues:
sudo usermod -aG docker $USER
# Or ensure hinahanan2003 is in docker group:
groups hinahanan2003
```

The workflow will automatically:
- Try operations without sudo first
- Fall back to sudo if permission denied
- Try with postgres user for git operations if needed
- Show warnings when sudo is used

### Post-Deployment Script Failures

```bash
# Check script logs
docker compose -f docker-compose.yml -f docker-compose.llm.yml logs api --tail=100
# Or with sudo if needed:
sudo docker compose -f docker-compose.yml -f docker-compose.llm.yml logs api --tail=100

# Run scripts manually to debug
docker compose -f docker-compose.yml -f docker-compose.llm.yml exec api python scripts/seed_real_protocols.py
# Or with sudo:
sudo docker compose -f docker-compose.yml -f docker-compose.llm.yml exec api python scripts/seed_real_protocols.py

# Check database state
docker compose -f docker-compose.yml -f docker-compose.llm.yml exec api python -c "
from app.database.connection import SessionLocal
from app.database.models import Protocol
db = SessionLocal()
print(f'Protocols: {db.query(Protocol).count()}')
db.close()
"
```

### GCS Permission Issues

```bash
# Verify service account has Storage Admin role
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:github-actions@YOUR_PROJECT.iam.gserviceaccount.com"

# Test GCS access
gsutil ls gs://YOUR_BUCKET_NAME/
```

### Deployment Failures

- **Check GitHub Actions logs**: Detailed error messages in Actions tab
- **Verify secrets are set correctly**: All required secrets must be configured
- **Test deployments manually first**: Run deployment scripts locally
- **Check VM disk space**: At least 5GB free required
- **Verify Docker resources**: Ensure Docker has enough memory/CPU
- **Check container logs**: `docker compose logs api --tail=100`
- **Verify database connectivity**: Check DATABASE_URL in .env file

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GCP Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [GCS Deployment Guide](https://cloud.google.com/storage/docs/hosting-static-website)




