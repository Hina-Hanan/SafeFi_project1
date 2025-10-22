# Frontend Deployment Guide

## ✅ Build Completed Successfully!

Your production build is ready in `frontend/dist/` folder.

**Build Summary:**
- Total size: ~923 kB
- Gzipped: ~282 kB
- Optimized chunks: vendor, mui, charts
- Minified with esbuild

---

## Step 1: Update API URL for Production

Before deploying, you need to update the API URL to point to your VM's external IP.

### A. Get Your VM's External IP

In your **SSH session** (VM), run:
```bash
curl ifconfig.me
```

Copy the IP address (e.g., `34.123.45.67`)

### B. Update the Production Build

In **PowerShell** (local machine), run:

```powershell
cd frontend

# Create .env.production file with your VM's IP
# Replace YOUR_VM_IP with the actual IP from step A
@"
VITE_API_BASE_URL=http://34.30.34.157:8000
"@ | Out-File -FilePath ".env.production" -Encoding UTF8

# Rebuild with production API URL
npm run build
```

**Example:**
```powershell
@"
VITE_API_BASE_URL=http://34.123.45.67:8000
"@ | Out-File -FilePath ".env.production" -Encoding UTF8
```

---

## Step 2: Deploy to Google Cloud Storage

### Option A: Deploy with gsutil (Recommended)

```powershell
# Set your GCP project ID
$env:PROJECT_ID = "SafeFi"

# Create a unique bucket name
$BUCKET_NAME = "safefi-tracking-$(Get-Date -Format 'yyyyMMddHHmmss')"

# Create bucket
gsutil mb gs://$BUCKET_NAME

# Make bucket public
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME

# Upload files
gsutil -m cp -r dist/* gs://$BUCKET_NAME/

# Configure for website hosting
gsutil web set -m index.html -e index.html gs://$BUCKET_NAME

# Get the public URL
echo "Frontend URL: https://storage.googleapis.com/$BUCKET_NAME/index.html"
```

### Option B: Deploy via GCP Console

1. Go to **Cloud Storage** in GCP Console
2. Click **Create Bucket**
   - Name: `safefi-frontend-YYYYMMDD`
   - Location: Same region as your VM
   - Storage class: Standard
   - Access control: Fine-grained
3. Click **Upload Folder** → Select `frontend/dist/`
4. After upload, go to **Bucket Details** → **Permissions**
5. Click **Add Principal**
   - New principal: `allUsers`
   - Role: `Storage Object Viewer`
6. Click **Save**
7. Access your app at: `https://storage.googleapis.com/safefi-frontend/index.html`

---

## Step 3: Update Backend CORS Settings

In your **SSH session** (VM), update CORS to allow your Cloud Storage domain:

```bash
# Switch to postgres user
sudo su - postgres

# Navigate to backend
cd ~/SafeFi_project1/backend

# Get your bucket name from previous step
BUCKET_NAME="your-bucket-name"

# Update .env file
cat >> .env << EOF

# Cloud Storage CORS
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://storage.googleapis.com
EOF

# Restart backend
sudo systemctl restart defi-backend

# Verify it's running
curl http://localhost:8000/health
```

---

## Step 4: Test Your Deployment

### A. Test Backend API
```bash
# In SSH session, get your external IP
curl ifconfig.me

# Test health endpoint from external IP
curl http://34.30.34.157:8000/health
```

### B. Test Frontend
1. Open your browser
2. Go to: `https://storage.googleapis.com/safefi/index.html`
3. You should see the DeFi Risk Assessment dashboard
4. Verify protocols load
5. Check AI Assistant works (if Ollama is running)

---

## Step 5: Optional - Set Up Custom Domain

### A. Using Cloud Load Balancer

```bash
# Reserve static IP
gcloud compute addresses create safefi-frontend-ip --global

# Get the IP
gcloud compute addresses describe safefi-frontend-ip --global

# Create backend bucket
gcloud compute backend-buckets create safefi-frontend-backend \
  --gcs-bucket-name=YOUR_BUCKET_NAME

# Create URL map
gcloud compute url-maps create safefi-frontend-map \
  --default-backend-bucket=safefi-frontend-backend

# Create HTTP proxy
gcloud compute target-http-proxies create safefi-frontend-proxy \
  --url-map=safefi-frontend-map

# Create forwarding rule
gcloud compute forwarding-rules create safefi-frontend-rule \
  --address=safefi-frontend-ip \
  --global \
  --target-http-proxy=safefi-frontend-proxy \
  --ports=80
```

### B. Configure DNS
1. Go to your domain registrar
2. Add an A record pointing to the reserved IP
3. Wait for DNS propagation (5-30 minutes)
4. Update CORS in backend to include your domain

---

## Step 6: Production Optimizations

### A. Enable CDN for Cloud Storage

```bash
# Enable CDN on your bucket
gcloud compute backend-buckets update safefi-frontend-backend \
  --enable-cdn
```

### B. Set Cache Headers

```bash
# Set cache headers for static assets
gsutil -m setmeta -h "Cache-Control:public, max-age=31536000" \
  "gs://YOUR_BUCKET_NAME/assets/**"

# Set cache headers for HTML
gsutil setmeta -h "Cache-Control:public, max-age=3600" \
  "gs://YOUR_BUCKET_NAME/index.html"
```

### C. Enable Compression

```bash
# Set content encoding for JS/CSS files
gsutil -m setmeta -h "Content-Encoding:gzip" \
  "gs://YOUR_BUCKET_NAME/assets/*.js"
```

---

## Troubleshooting

### Frontend doesn't load
- Check browser console for errors
- Verify API URL is correct in .env.production
- Check CORS settings on backend

### API calls fail
- Verify VM firewall allows port 8000
- Check backend is running: `sudo systemctl status defi-backend`
- Test API directly: `curl http://VM_IP:8000/health`

### CORS errors
- Update backend .env CORS_ORIGINS to include storage.googleapis.com
- Restart backend: `sudo systemctl restart defi-backend`
- Clear browser cache

### 404 errors on Cloud Storage
- Verify all files uploaded: `gsutil ls gs://YOUR_BUCKET_NAME/`
- Check bucket permissions: `gsutil iam get gs://YOUR_BUCKET_NAME/`
- Verify web configuration: `gsutil web get gs://YOUR_BUCKET_NAME/`

---

## Success Checklist

- [ ] Build completed without errors
- [ ] .env.production created with VM IP
- [ ] Production build created with correct API URL
- [ ] Cloud Storage bucket created
- [ ] Files uploaded to bucket
- [ ] Bucket made public
- [ ] Website hosting enabled
- [ ] Backend CORS updated
- [ ] Backend restarted
- [ ] Frontend loads in browser
- [ ] API calls work
- [ ] Protocols display correctly
- [ ] AI Assistant responds (if Ollama running)

---

## Quick Reference

### Your URLs
- **Backend API**: `http://YOUR_VM_IP:8000`
- **Frontend**: `https://storage.googleapis.com/YOUR_BUCKET_NAME/index.html`
- **API Docs**: `http://YOUR_VM_IP:8000/docs`

### Useful Commands

```bash
# Rebuild frontend (after changes)
cd frontend && npm run build

# Redeploy to Cloud Storage
gsutil -m rsync -r dist/ gs://YOUR_BUCKET_NAME/

# Check backend health
curl http://YOUR_VM_IP:8000/health

# View backend logs
sudo journalctl -u defi-backend -f

# Restart backend
sudo systemctl restart defi-backend
```

---

## Next Steps

1. ✅ Monitor application performance
2. ✅ Set up Google Cloud Monitoring
3. ✅ Configure alerts for downtime
4. ✅ Set up automated backups
5. ✅ Add SSL/HTTPS with Cloud Load Balancer
6. ✅ Configure custom domain
7. ✅ Implement CI/CD pipeline

Your DeFi Risk Assessment application is now production-ready! 🚀







