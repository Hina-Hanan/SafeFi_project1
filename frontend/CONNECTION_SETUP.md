# Frontend-Backend Connection Setup
# Your VM IP: 34.30.34.157

## ✅ API Configuration Updated

Your `frontend/src/services/api.ts` has been updated to use your VM IP:
- **Production**: `http://34.30.34.157:8000`
- **Development**: `http://127.0.0.1:8000`

## 🧪 Test the Connection

### 1. Test Backend from VM:
```bash
# On your VM
curl http://34.30.34.157:8000/health
curl http://34.30.34.157:8000/protocols
```

### 2. Test Backend from Your Local Machine:
```bash
# From Windows (your local machine)
curl http://34.30.34.157:8000/health
curl http://34.30.34.157:8000/protocols
```

### 3. Build and Test Frontend:
```bash
# On your VM
cd ~/SafeFi_project1/frontend
npm run build
npm run dev
```

## 🔧 Environment Variable (Optional)

If you want to override the API URL, create `frontend/.env`:
```
VITE_API_BASE_URL=http://34.30.34.157:8000
```

## 🌐 Frontend Deployment

After building, deploy to Cloud Storage:
1. Upload `frontend/dist/` contents to Cloud Storage bucket
2. Make bucket public
3. Access via: `https://storage.googleapis.com/your-bucket-name/index.html`

## 🔍 Troubleshooting

If frontend can't connect to backend:
1. Check if backend is running: `sudo systemctl status defi-backend`
2. Check firewall: Ensure port 8000 is open in GCP
3. Test direct connection: `curl http://34.30.34.157:8000/health`

## 📊 Current Status
- ✅ Backend running on VM
- ✅ API configuration updated
- ✅ VM IP: 34.30.34.157
- ✅ Port: 8000
- 🔄 Ready for frontend testing


