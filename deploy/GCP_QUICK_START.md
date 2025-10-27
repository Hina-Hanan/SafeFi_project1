# Quick Start: Deploy SafeFi to GCP (safefi.live)

**Complete step-by-step instructions to deploy your live application**

## Prerequisites

- [ ] Google Cloud Platform account with billing enabled
- [ ] Domain: safefi.live (already configured)
- [ ] Google Cloud SDK installed on your local machine
- [ ] Git repository access

## Step-by-Step Instructions

### Step 1: Initial GCP Setup (Run Once)

From your **local machine**:

```bash
# 1. Install Google Cloud SDK (if not already installed)
# Visit: https://cloud.google.com/sdk/docs/install

# 2. Login to GCP
gcloud auth login

# 3. Set your project
gcloud config set project YOUR_PROJECT_ID

# 4. Enable Compute Engine API
gcloud services enable compute.googleapis.com
```

### Step 2: Automated VM and Infrastructure Setup

Run the automated setup script from your **local machine**:

```bash
cd deploy
chmod +x quick-gcp-setup.sh
./quick-gcp-setup.sh
```

This script will:
- ✅ Create VM instance (e2-medium, 50GB disk)
- ✅ Configure firewall rules
- ✅ Install Docker and Docker Compose
- ✅ Install Nginx and Certbot

**Time**: ~5-10 minutes

### Step 3: SSH to VM

```bash
gcloud compute ssh safefi-production --zone=us-central1-a
```

### Step 4: Clone Repository

On the **VM**:

```bash
# Navigate to /opt directory
cd /opt

# Clone your repository (replace with your repo URL)
git clone https://github.com/your-username/safefi.git

# Set permissions
sudo chown -R $USER:$USER /opt/safefi

# Navigate to deploy directory
cd safefi/deploy
```

### Step 5: Configure Environment

Create `.env.production` file:

```bash
nano .env.production
```

Add this configuration:

```bash
# Production Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database - CHANGE THIS PASSWORD!
POSTGRES_USER=defi_user
POSTGRES_PASSWORD=YourSecurePassword123!
POSTGRES_DB=defi_risk_assessment

# API
API_PORT=8000
CORS_ORIGINS=https://safefi.live,https://www.safefi.live,https://api.safefi.live

# Frontend
FRONTEND_PORT=80

# MLflow
MLFLOW_PORT=5000

# Email (optional)
EMAIL_ALERTS_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
ALERT_SENDER_EMAIL=
ALERT_SENDER_PASSWORD=
```

**Save and exit**: `Ctrl+X`, then `Y`, then `Enter`

### Step 6: Get VM External IP

```bash
# Get external IP
gcloud compute instances describe safefi-production --zone=us-central1-a --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

**Copy this IP address** - you'll need it for DNS configuration.

### Step 7: Configure DNS

Go to your DNS provider (where safefi.live is hosted):

1. **Add A records:**
   - `safefi.live` → [VM_EXTERNAL_IP]
   - `www.safefi.live` → [VM_EXTERNAL_IP]
   - `api.safefi.live` → [VM_EXTERNAL_IP]

2. **Wait for DNS propagation** (usually 5-15 minutes)

### Step 8: Setup SSL Certificates

Still on the **VM**:

```bash
# Install nginx configuration (we'll create this)
sudo nano /etc/nginx/sites-available/safefi
```

**Copy-paste this configuration** (Ctrl+Shift+V to paste):

```nginx
# Frontend
server {
    listen 80;
    server_name safefi.live www.safefi.live;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name safefi.live www.safefi.live;
    
    location / {
        proxy_pass http://localhost:80;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Backend API
server {
    listen 80;
    server_name api.safefi.live;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.safefi.live;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Save** (Ctrl+X, Y, Enter)

Enable and test configuration:

```bash
sudo ln -s /etc/nginx/sites-available/safefi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 9: Get SSL Certificates

```bash
# Get SSL for frontend domain
sudo certbot --nginx -d safefi.live -d www.safefi.live

# Get SSL for API domain
sudo certbot --nginx -d api.safefi.live

# Follow the prompts (choose option 1 to redirect HTTP to HTTPS)
```

### Step 10: Deploy Application

```bash
# Navigate to project root (not deploy directory)
cd /opt/safefi

# Make scripts executable
chmod +x deploy/*.sh

# Deploy
cd deploy
./deploy.sh
```

**Wait** for the deployment to complete (~2-3 minutes)

### Step 11: Verify Deployment

```bash
# Run health checks
./health-check.sh

# View running containers
docker ps

# View logs
docker-compose logs -f
```

### Step 12: Access Your Application

Open in browser:
- **Frontend**: https://safefi.live
- **Backend API**: https://api.safefi.live
- **API Documentation**: https://api.safefi.live/docs

## Setup Auto-Deployment from GitHub

### Configure GitHub Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add these secrets:

```
Name: PROD_HOST
Value: [Your VM external IP]

Name: PROD_USER
Value: [Your GCP username]

Name: PROD_SSH_KEY
Value: [Your SSH private key content]
```

To get SSH key:
```bash
# On your local machine
cat ~/.ssh/google_compute_engine
# Copy the entire output to PROD_SSH_KEY secret
```

### Now Auto-Deploy!

Every time you push to `main` branch:
```bash
git add .
git commit -m "Update application"
git push origin main
```

GitHub Actions will automatically:
1. Run tests
2. Build Docker images
3. Deploy to your GCP VM
4. Verify deployment

## Maintenance Commands

### View Logs
```bash
docker-compose logs -f
```

### Update Application
```bash
cd /opt/safefi
git pull
cd deploy
./deploy.sh
```

### Restart Services
```bash
docker-compose restart
```

### Stop Services
```bash
docker-compose down
```

### Start Services
```bash
docker-compose up -d
```

### Access Database
```bash
docker exec -it safefi-db psql -U defi_user -d defi_risk_assessment
```

## Troubleshooting

### Cannot access https://safefi.live

1. Check DNS propagation:
   ```bash
   nslookup safefi.live
   ```

2. Check nginx status:
   ```bash
   sudo systemctl status nginx
   sudo nginx -t
   ```

3. Check containers:
   ```bash
   docker ps
   ```

### Services not starting

1. View logs:
   ```bash
   docker-compose logs api
   docker-compose logs frontend
   ```

2. Check resources:
   ```bash
   htop
   free -h
   df -h
   ```

### SSL Certificate Issues

```bash
# Renew certificates
sudo certbot renew

# Force renewal
sudo certbot renew --force-renewal

# Reload nginx
sudo systemctl reload nginx
```

## Cost Estimation

**VM (e2-medium, 50GB disk)**: ~$30-40/month
- 2 vCPU
- 4GB RAM
- 50GB SSD storage

## Security Checklist

- [ ] Changed default database password
- [ ] SSL certificates installed and auto-renewing
- [ ] Firewall rules configured
- [ ] Nginx security headers enabled
- [ ] Regular backups configured
- [ ] Log monitoring setup
- [ ] Automatic security updates enabled

## Next Steps

1. **Monitor Application**: Set up Cloud Monitoring
2. **Setup Backups**: Configure automated database backups
3. **Load Balancing**: Add load balancer for high availability
4. **CDN**: Setup Cloud CDN for static assets
5. **Monitoring**: Add application performance monitoring

## Support

- Full documentation: `CICD.md`
- GCP guide: `deploy/GCP_DEPLOYMENT_GUIDE.md`
- Deployment scripts: `deploy/README.md`

---

**Your application is now live at https://safefi.live! 🎉**
