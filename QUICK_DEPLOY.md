# 🚀 Quick Deploy - 3 Commands

## Your Application is Built and Ready!

Frontend is compiled in `frontend/dist/` folder.

---

## Deploy in 3 Steps

### Step 1: Get Your VM's External IP

In **SSH-in-browser** (your VM):
```bash
curl ifconfig.me
```

Copy the IP address (e.g., `34.123.45.67`)

---

### Step 2: Deploy Frontend

In **PowerShell** (your local machine):

```powershell
# Replace with YOUR values:
# - VM_IP: from step 1
# - PROJECT_ID: your GCP project ID

.\deploy\deploy_frontend.ps1 -VM_IP "34.123.45.67" -PROJECT_ID "my-gcp-project"
```

This will:
- ✅ Configure production API URL
- ✅ Rebuild frontend
- ✅ Create Cloud Storage bucket
- ✅ Upload files
- ✅ Make it public
- ✅ Give you the live URL

---

### Step 3: Update CORS

In **SSH-in-browser** (your VM):

```bash
sudo su - postgres
cd ~/SafeFi_project1/backend

cat >> .env << 'EOF'

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://storage.googleapis.com
EOF

sudo systemctl restart defi-backend
```

---

## ✅ Done!

Open the URL from Step 2 in your browser.

Your DeFi Risk Assessment platform is LIVE! 🎉

---

## Alternative: Manual Deploy

If you prefer step-by-step manual deployment:

### 1. Update API URL
```powershell
cd frontend
@"
VITE_API_BASE_URL=http://YOUR_VM_IP:8000
"@ | Out-File -FilePath ".env.production" -Encoding UTF8
```

### 2. Rebuild
```powershell
npm run build
```

### 3. Create Bucket
```powershell
$BUCKET = "safefi-frontend-$(Get-Date -Format 'yyyyMMddHHmmss')"
gsutil mb gs://$BUCKET
gsutil iam ch allUsers:objectViewer gs://$BUCKET
```

### 4. Upload Files
```powershell
gsutil -m cp -r dist/* gs://$BUCKET/
gsutil web set -m index.html -e index.html gs://$BUCKET
```

### 5. Access
```
https://storage.googleapis.com/$BUCKET/index.html
```

---

## Need Help?

See `PRODUCTION_READY.md` for full details.





