# Frontend HTTPS Configuration for GCP Deployment
# This file contains the configuration needed to fix Mixed Content errors

## Problem
Mixed Content errors occur when:
- Frontend is served over HTTPS (GCP default)
- Backend API calls are made over HTTP
- Browser blocks insecure requests

## Solution
1. Update frontend API calls to use HTTPS
2. Configure GCP Load Balancer for HTTPS
3. Set up SSL certificates

## Files Modified
- frontend/src/services/api.ts: Updated to use HTTPS in production
- Added automatic detection of production vs development environment

## GCP Deployment Steps
1. Get your VM's external IP address
2. Update the IP in frontend/src/services/api.ts (line 15)
3. Configure GCP Load Balancer with SSL certificate
4. Deploy frontend to Cloud Storage with HTTPS

## Testing
After deployment, test with:
```bash
curl https://your-frontend-domain.com
curl https://your-vm-ip:8000/health
```

## Environment Variables
For production deployment, set:
- VITE_API_BASE_URL=https://your-vm-ip:8000
- VITE_NODE_ENV=production


