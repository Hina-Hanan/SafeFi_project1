#!/bin/bash

# Apply Nginx configuration for safefi.live domain
# Run this script on your VM

set -e

echo "🔧 Updating Nginx configuration for safefi.live domain..."

# Copy the new configuration
sudo cp /var/lib/postgresql/SafeFi_project1/deploy/nginx_safefi_config.conf /etc/nginx/sites-available/safefi.live

# Remove old configuration
sudo rm -f /etc/nginx/sites-available/defi-backend
sudo rm -f /etc/nginx/sites-enabled/defi-backend

# Enable new configuration
sudo ln -sf /etc/nginx/sites-available/safefi.live /etc/nginx/sites-enabled/

# Test Nginx configuration
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid!"
    
    # Reload Nginx
    echo "🔄 Reloading Nginx..."
    sudo systemctl reload nginx
    
    echo "✅ Nginx configuration updated successfully!"
    echo "🌐 Your app will be available at:"
    echo "   - Frontend: https://safefi.live"
    echo "   - API: https://api.safefi.live"
else
    echo "❌ Nginx configuration test failed!"
    exit 1
fi
