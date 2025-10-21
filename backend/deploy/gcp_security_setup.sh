#!/bin/bash

# GCP Security Setup for DeFi Risk Assessment Platform
# This script enhances security for production deployment

set -e

echo "🔒 Setting up GCP Security for DeFi Risk Assessment Platform"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Update system and install security tools
print_status "Installing security tools..."
sudo apt-get update
sudo apt-get install -y fail2ban ufw unattended-upgrades

# 2. Configure firewall
print_status "Configuring firewall..."
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow only necessary ports
sudo ufw allow ssh
sudo ufw allow 8000/tcp  # Backend API
sudo ufw allow 5173/tcp  # Frontend (if needed)
sudo ufw allow 5000/tcp  # MLflow (optional)

print_status "Firewall configured. Open ports: SSH, 8000, 5173, 5000"

# 3. Configure fail2ban for SSH protection
print_status "Configuring fail2ban..."
sudo tee /etc/fail2ban/jail.local > /dev/null <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# 4. Set up automatic security updates
print_status "Configuring automatic security updates..."
sudo tee /etc/apt/apt.conf.d/50unattended-upgrades > /dev/null <<EOF
Unattended-Upgrade::Allowed-Origins {
    "\${distro_id}:\${distro_codename}-security";
    "\${distro_id}ESMApps:\${distro_codename}-apps-security";
    "\${distro_id}ESM:\${distro_codename}-infra-security";
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF

sudo tee /etc/apt/apt.conf.d/20auto-upgrades > /dev/null <<EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF

# 5. Create non-root user for application
print_status "Creating application user..."
sudo useradd -m -s /bin/bash defi-app || true
sudo usermod -aG sudo defi-app

# 6. Set up application directory with proper permissions
print_status "Setting up application directory..."
sudo mkdir -p /opt/defi-risk-assessment
sudo chown defi-app:defi-app /opt/defi-risk-assessment

# 7. Configure log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/defi-risk-assessment > /dev/null <<EOF
/opt/defi-risk-assessment/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 defi-app defi-app
    postrotate
        systemctl reload defi-risk-assessment || true
    endscript
}
EOF

# 8. Create systemd service for the application
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/defi-risk-assessment.service > /dev/null <<EOF
[Unit]
Description=DeFi Risk Assessment Platform
After=network.target postgresql.service

[Service]
Type=simple
User=defi-app
Group=defi-app
WorkingDirectory=/opt/defi-risk-assessment
Environment=PATH=/opt/defi-risk-assessment/venv/bin
ExecStart=/opt/defi-risk-assessment/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=defi-risk-assessment

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/defi-risk-assessment
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

[Install]
WantedBy=multi-user.target
EOF

# 9. Create cron job for automatic updates
print_status "Setting up automatic risk updates..."
sudo tee /etc/cron.d/defi-risk-updates > /dev/null <<EOF
# DeFi Risk Assessment - Automatic Updates
# Runs every 5 hours
0 */5 * * * defi-app cd /opt/defi-risk-assessment && /opt/defi-risk-assessment/venv/bin/python scripts/auto_update_risks.py >> /opt/defi-risk-assessment/logs/auto_update.log 2>&1
EOF

# 10. Set up monitoring and alerting
print_status "Setting up basic monitoring..."
sudo apt-get install -y htop iotop nethogs

# Create monitoring script
sudo tee /opt/defi-risk-assessment/monitor.sh > /dev/null <<'EOF'
#!/bin/bash
# Basic monitoring script

LOG_FILE="/opt/defi-risk-assessment/logs/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check if application is running
if ! pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "[$DATE] WARNING: Application not running" >> $LOG_FILE
    systemctl restart defi-risk-assessment
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$DATE] WARNING: Disk usage at ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEM_USAGE -gt 90 ]; then
    echo "[$DATE] WARNING: Memory usage at ${MEM_USAGE}%" >> $LOG_FILE
fi
EOF

sudo chmod +x /opt/defi-risk-assessment/monitor.sh

# Add monitoring to cron (every 5 minutes)
sudo tee -a /etc/cron.d/defi-risk-updates > /dev/null <<EOF

# Monitoring check every 5 minutes
*/5 * * * * defi-app /opt/defi-risk-assessment/monitor.sh
EOF

# 11. Create backup script
print_status "Setting up backup script..."
sudo tee /opt/defi-risk-assessment/backup.sh > /dev/null <<'EOF'
#!/bin/bash
# Backup script for DeFi Risk Assessment

BACKUP_DIR="/opt/defi-risk-assessment/backups"
DATE=$(date '+%Y%m%d_%H%M%S')
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.tar.gz"

mkdir -p $BACKUP_DIR

# Backup database
pg_dump defi_risk_assessment > /tmp/db_backup.sql

# Create backup archive
tar -czf $BACKUP_FILE -C /opt/defi-risk-assessment \
    --exclude='venv' \
    --exclude='logs' \
    --exclude='backups' \
    --exclude='__pycache__' \
    . /tmp/db_backup.sql

# Clean up old backups (keep last 7 days)
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete

echo "Backup created: $BACKUP_FILE"
EOF

sudo chmod +x /opt/defi-risk-assessment/backup.sh

# Add backup to cron (daily at 2 AM)
sudo tee -a /etc/cron.d/defi-risk-updates > /dev/null <<EOF

# Daily backup at 2 AM
0 2 * * * defi-app /opt/defi-risk-assessment/backup.sh >> /opt/defi-risk-assessment/logs/backup.log 2>&1
EOF

# 12. Set proper permissions
print_status "Setting up permissions..."
sudo chown -R defi-app:defi-app /opt/defi-risk-assessment
sudo chmod -R 755 /opt/defi-risk-assessment
sudo chmod 600 /opt/defi-risk-assessment/.env

# 13. Create logs directory
sudo mkdir -p /opt/defi-risk-assessment/logs
sudo chown defi-app:defi-app /opt/defi-risk-assessment/logs

print_status "Security setup completed!"
echo ""
echo "🔒 Security Features Enabled:"
echo "  ✅ Firewall configured (only necessary ports open)"
echo "  ✅ Fail2ban protection against brute force"
echo "  ✅ Automatic security updates"
echo "  ✅ Non-root application user"
echo "  ✅ Systemd service with security restrictions"
echo "  ✅ Log rotation"
echo "  ✅ Automatic monitoring"
echo "  ✅ Daily backups"
echo "  ✅ Cron jobs for updates and monitoring"
echo ""
echo "📋 Next Steps:"
echo "  1. Deploy your application to /opt/defi-risk-assessment"
echo "  2. Run: sudo systemctl enable defi-risk-assessment"
echo "  3. Run: sudo systemctl start defi-risk-assessment"
echo "  4. Check logs: journalctl -u defi-risk-assessment -f"
echo ""
echo "🔍 Monitoring:"
echo "  - Application logs: journalctl -u defi-risk-assessment"
echo "  - Update logs: tail -f /opt/defi-risk-assessment/logs/auto_update.log"
echo "  - Monitor logs: tail -f /opt/defi-risk-assessment/logs/monitor.log"
echo ""

