# GCP Deployment Guide for SafeFi

Complete step-by-step guide to deploy SafeFi to Google Cloud Platform.

## Prerequisites

1. GCP account with billing enabled
2. Google Cloud SDK installed
3. Domain: safefi.live (already configured)
4. SSH access to GCP VM

## Step 1: Create GCP VM Instance

### 1.1 Create VM via Console

1. Go to [GCP Console](https://console.cloud.google.com/)
2. Navigate to **Compute Engine > VM Instances**
3. Click **Create Instance**

### 1.2 VM Configuration

```
Name: safefi-production
Machine Type: e2-medium (2 vCPU, 4GB RAM)
Zone: us-central1-a (or your preferred zone)

Boot disk:
  - OS: Ubuntu 22.04 LTS
  - Disk size: 50GB SSD

Firewall:
  - Allow HTTP traffic
  - Allow HTTPS traffic

Network tags: safefi-app
```

### 1.3 Create VM via CLI

```bash
gcloud compute instances create safefi-production \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --network-interface=network-tier=PREMIUM,subnet=default \
  --maintenance-policy=MIGRATE \
  --provisioning-model=STANDARD \
  --service-account=YOUR_SERVICE_ACCOUNT \
  --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
  --tags=http-server,https-server \
  --create-disk=auto-delete=yes,boot=yes,device-name=safefi-production,image=projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20231116,mode=rw,size=50,type=projects/YOUR_PROJECT_ID/zones/us-central1-a/diskTypes/pd-balanced \
  --reservation-affinity=any
```

## Step 2: Configure Firewall Rules

### 2.1 Allow HTTP/HTTPS Traffic

```bash
# HTTP
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 \
  --source-ranges 0.0.0.0/0 \
  --target-tags http-server \
  --description "Allow HTTP traffic for SafeFi"

# HTTPS
gcloud compute firewall-rules create allow-https \
  --allow tcp:443 \
  --source-ranges 0.0.0.0/0 \
  --target-tags https-server \
  --description "Allow HTTPS traffic for SafeFi"

# Backend API
gcloud compute firewall-rules create allow-backend \
  --allow tcp:8000 \
  --source-ranges 0.0.0.0/0 \
  --target-tags safefi-app \
  --description "Allow Backend API access"
```

## Step 3: Connect to VM and Setup

### 3.1 SSH to VM

```bash
gcloud compute ssh safefi-production --zone=us-central1-a
```

### 3.2 Install Docker and Docker Compose

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt-get install -y git

# Install required tools
sudo apt-get install -y curl wget nano
```

### 3.3 Install Nginx (for reverse proxy)

```bash
sudo apt-get install -y nginx
sudo systemctl enable nginx
```

## Step 4: Setup Domain and SSL

### 4.1 Point Domain to VM IP

1. Get VM external IP:
   ```bash
   gcloud compute instances describe safefi-production --zone=us-central1-a --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
   ```

2. Update DNS records:
   ```
   A record: safefi.live → [VM_EXTERNAL_IP]
   A record: api.safefi.live → [VM_EXTERNAL_IP]
   ```

### 4.2 Install Certbot for SSL

```bash
sudo apt-get install -y certbot python3-certbot-nginx
```

### 4.3 Setup SSL Certificates

```bash
# For safefi.live
sudo certbot --nginx -d safefi.live -d www.safefi.live

# For api.safefi.live
sudo certbot --nginx -d api.safefi.live
```

## Step 5: Configure Nginx

### 5.1 Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/safefi
```

### 5.2 Add Configuration

```nginx
# Frontend configuration
server {
    listen 80;
    server_name safefi.live www.safefi.live;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name safefi.live www.safefi.live;

    ssl_certificate /etc/letsencrypt/live/safefi.live/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/safefi.live/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Proxy to frontend container
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

# API Backend configuration
server {
    listen 80;
    server_name api.safefi.live;

    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.safefi.live;

    ssl_certificate /etc/letsencrypt/live/api.safefi.live/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.safefi.live/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Proxy to backend API
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

### 5.3 Enable Configuration

```bash
sudo ln -s /etc/nginx/sites-available/safefi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Step 6: Clone and Setup Application

### 6.1 Clone Repository

```bash
cd /opt
sudo git clone https://github.com/your-username/safefi.git
sudo chown -R $USER:$USER /opt/safefi
cd /opt/safefi
```

### 6.2 Create Production Environment File

```bash
cd deploy
nano .env.production
```

```bash
# Production Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database
POSTGRES_USER=defi_user
POSTGRES_PASSWORD=YOUR_SECURE_PASSWORD_HERE
POSTGRES_DB=defi_risk_assessment

# API
API_PORT=8000
CORS_ORIGINS=https://safefi.live,https://www.safefi.live

# Frontend
FRONTEND_PORT=80

# MLflow
MLFLOW_PORT=5000

# Email (optional)
EMAIL_ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
ALERT_SENDER_EMAIL=your-email@gmail.com
ALERT_SENDER_PASSWORD=your-app-password
```

## Step 7: Deploy Application

### 7.1 Build and Start Services

```bash
cd /opt/safefi
docker-compose build
docker-compose up -d
```

### 7.2 Run Database Migrations

```bash
docker-compose exec api alembic upgrade head
```

### 7.3 Verify Deployment

```bash
# Check containers
docker ps

# Check logs
docker-compose logs -f

# Health checks
curl http://localhost:80/health
curl http://localhost:8000/health
```

## Step 8: Setup Auto-Start on Reboot

### 8.1 Create Systemd Service

```bash
sudo nano /etc/systemd/system/safefi.service
```

```ini
[Unit]
Description=SafeFi Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/safefi
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

### 8.2 Enable Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable safefi.service
sudo systemctl start safefi.service
```

## Step 9: Configure GitHub Actions for Auto-Deployment

### 9.1 Add GCP Secrets to GitHub

Go to your GitHub repository settings:
- Settings → Secrets → Actions

Add these secrets:
```
PROD_HOST: [YOUR_VM_EXTERNAL_IP]
PROD_USER: [YOUR_VM_USERNAME]
PROD_SSH_KEY: [YOUR_SSH_PRIVATE_KEY]
PROD_PORT: 22
```

### 9.2 Update Deploy Workflow

The `.github/workflows/deploy.yml` will automatically deploy when you push to main.

## Step 10: Monitoring and Maintenance

### 10.1 View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker logs safefi-api -f
docker logs safefi-frontend -f
```

### 10.2 Access Services

- **Frontend**: https://safefi.live
- **Backend API**: https://api.safefi.live
- **API Docs**: https://api.safefi.live/docs
- **MLflow**: https://api.safefi.live:5000

### 10.3 Backup Database

```bash
# Create backup script
nano /opt/safefi-backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
mkdir -p $BACKUP_DIR

docker exec safefi-db pg_dump -U defi_user defi_risk_assessment > $BACKUP_DIR/safefi_backup_$DATE.sql

# Keep only last 30 days of backups
find $BACKUP_DIR -name "safefi_backup_*.sql" -mtime +30 -delete
```

```bash
chmod +x /opt/safefi-backup.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /opt/safefi-backup.sh
```

## Step 11: Update Application

### 11.1 Manual Update

```bash
cd /opt/safefi
git pull origin main
docker-compose build
docker-compose up -d
docker-compose exec api alembic upgrade head
```

### 11.2 Automatic Update via CI/CD

Just push to main branch:
```bash
git add .
git commit -m "Update application"
git push origin main
```

## Quick Reference Commands

```bash
# SSH to VM
gcloud compute ssh safefi-production --zone=us-central1-a

# View VM status
gcloud compute instances describe safefi-production --zone=us-central1-a

# Stop VM
gcloud compute instances stop safefi-production --zone=us-central1-a

# Start VM
gcloud compute instances start safefi-production --zone=us-central1-a

# View disk usage
df -h

# Monitor resources
htop

# View Docker containers
docker ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Update application
cd /opt/safefi && git pull && docker-compose build && docker-compose up -d
```

## Security Checklist

- [ ] Changed default passwords
- [ ] SSL certificates installed and auto-renewing
- [ ] Firewall rules configured
- [ ] Database backups automated
- [ ] Monitoring enabled
- [ ] Log rotation configured
- [ ] SSH key-based authentication only
- [ ] Automatic security updates enabled

## Troubleshooting

### Issue: Cannot access application

```bash
# Check firewall
gcloud compute firewall-rules list

# Check nginx
sudo systemctl status nginx
sudo nginx -t

# Check containers
docker ps
docker-compose logs
```

### Issue: SSL certificate expired

```bash
# Renew certificate
sudo certbot renew
sudo systemctl reload nginx
```

### Issue: Out of disk space

```bash
# Clean Docker
docker system prune -a

# Clean old backups
find /opt/backups -name "*.sql" -mtime +30 -delete
```

### Issue: Container won't start

```bash
# Check logs
docker-compose logs api

# Restart service
docker-compose restart api
```

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Check system resources: `htop`
3. Check nginx: `sudo systemctl status nginx`
4. Review documentation: `CICD.md`
