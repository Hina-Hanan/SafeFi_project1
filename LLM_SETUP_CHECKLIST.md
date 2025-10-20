# ✅ LLM Setup Checklist

## Your 2-Hour Path to Working LLM

---

## Phase 1: Cleanup (5 minutes)

### Local Machine Cleanup

- [ ] Stop Ollama if running
  ```bash
  # Windows: taskkill /F /IM ollama.exe
  # Mac/Linux: pkill ollama
  ```

- [ ] Remove Mistral model
  ```bash
  ollama rm mistral
  ollama rm nomic-embed-text
  ```

- [ ] (Optional) Uninstall Ollama completely
  ```bash
  # Windows: winget uninstall Ollama.Ollama
  # Mac: brew uninstall ollama
  ```

- [ ] (Optional) Uninstall ngrok
  ```bash
  # Windows: winget uninstall ngrok
  # Mac: brew uninstall ngrok
  ```

**✅ Space freed: ~5GB**

---

## Phase 2: GCP Setup (30 minutes)

### Step 1: Create GCP Project

- [ ] Go to [console.cloud.google.com](https://console.cloud.google.com)
- [ ] Create new project: `defi-risk-assessment`
- [ ] Enable Compute Engine API
- [ ] Note: You have $300 free credit

### Step 2: Create VM Instance

- [ ] Name: `defi-backend`
- [ ] Region: `us-central1-a` (free tier eligible)
- [ ] Machine: `e2-medium` (2 vCPU, 4GB RAM)
- [ ] OS: Ubuntu 22.04 LTS
- [ ] Disk: 30GB Standard
- [ ] Firewall: ✅ HTTP, ✅ HTTPS

### Step 3: Configure Firewall

- [ ] Create rule: `allow-backend-8000`
- [ ] Protocol: TCP
- [ ] Port: 8000
- [ ] Source: 0.0.0.0/0

### Step 4: Note Information

- [ ] External IP: `___.___.___. ___`
- [ ] Zone: `us-central1-a`
- [ ] Project ID: `________________`

---

## Phase 3: Automated Installation (40 minutes)

### Step 1: SSH into Instance

- [ ] Click "SSH" button in GCP console
  ```bash
  # Or via CLI:
  gcloud compute ssh defi-backend --zone=us-central1-a
  ```

### Step 2: Run Setup Script

- [ ] Download script:
  ```bash
  curl -O https://raw.githubusercontent.com/YOUR_REPO/main/backend/deploy/gcp_tinyllama_setup.sh
  chmod +x gcp_tinyllama_setup.sh
  ```

- [ ] Run script:
  ```bash
  ./gcp_tinyllama_setup.sh
  ```

- [ ] Enter GitHub repo URL when prompted

- [ ] Wait for completion (30-40 minutes)
  - [ ] Python installed
  - [ ] PostgreSQL configured
  - [ ] Ollama installed
  - [ ] TinyLlama pulled (1.1GB)
  - [ ] Embedding model pulled
  - [ ] Backend configured
  - [ ] Services started

- [ ] Save database password from: `~/db_password.txt`

---

## Phase 4: Initialization (10 minutes)

### Initialize Vector Store

- [ ] Still in SSH, run:
  ```bash
  curl -X POST http://localhost:8000/api/v1/llm/initialize
  ```

- [ ] Wait for completion (5-10 minutes)

- [ ] Expected output:
  ```json
  {
    "initialized": true,
    "document_count": XX,
    "message": "Vector store initialized successfully"
  }
  ```

---

## Phase 5: Testing (10 minutes)

### Local Tests (on GCP instance)

- [ ] Test backend health:
  ```bash
  curl http://localhost:8000/api/v1/health
  ```
  Expected: `{"status":"ok","database_connected":true}`

- [ ] Test LLM health:
  ```bash
  curl http://localhost:8000/api/v1/llm/health
  ```
  Expected: `{"ollama_available":true,"vector_store_initialized":true}`

- [ ] Test LLM query:
  ```bash
  curl -X POST http://localhost:8000/api/v1/llm/query \
    -H "Content-Type: application/json" \
    -d '{"query":"Hello"}'
  ```
  Expected: JSON response with "answer" field

### Remote Tests (from your local machine)

- [ ] Test from local computer:
  ```bash
  export GCP_IP=YOUR_EXTERNAL_IP
  curl http://$GCP_IP:8000/api/v1/health
  ```

- [ ] Test LLM remotely:
  ```bash
  curl http://$GCP_IP:8000/api/v1/llm/health
  ```

- [ ] Test query remotely:
  ```bash
  curl -X POST http://$GCP_IP:8000/api/v1/llm/query \
    -H "Content-Type: application/json" \
    -d '{"query":"What protocols are monitored?"}'
  ```

### Run Test Script

- [ ] Download and run test script:
  ```bash
  curl -O https://raw.githubusercontent.com/YOUR_REPO/main/backend/deploy/test_gcp_deployment.sh
  chmod +x test_gcp_deployment.sh
  ./test_gcp_deployment.sh
  ```

- [ ] All tests should pass ✅

---

## Phase 6: Verification (5 minutes)

### Service Status

- [ ] SSH into GCP
- [ ] Check backend service:
  ```bash
  sudo systemctl status defi-backend
  ```
  Expected: `active (running)`

- [ ] Check Ollama service:
  ```bash
  sudo systemctl status ollama
  ```
  Expected: `active (running)`

### Access URLs

- [ ] API URL: `http://YOUR_GCP_IP:8000`
- [ ] API Docs: `http://YOUR_GCP_IP:8000/docs`
- [ ] Health Check: `http://YOUR_GCP_IP:8000/api/v1/health`
- [ ] LLM Health: `http://YOUR_GCP_IP:8000/api/v1/llm/health`

---

## ✅ Success Criteria

All of these should be ✅:

- [ ] GCP instance is running
- [ ] Backend service is active
- [ ] Ollama service is active
- [ ] Database is connected
- [ ] Vector store is initialized
- [ ] Health checks pass locally
- [ ] Health checks pass remotely
- [ ] LLM queries return valid answers
- [ ] API documentation is accessible

---

## 📝 Important Information to Save

**GCP Details:**
- External IP: `_______________`
- Project ID: `_______________`
- Zone: `us-central1-a`

**Access URLs:**
- API: `http://YOUR_IP:8000`
- Docs: `http://YOUR_IP:8000/docs`

**Credentials:**
- Database password: Saved in `~/db_password.txt` on GCP
- GitHub repo: `_______________`

**Services:**
- Backend logs: `sudo journalctl -u defi-backend -f`
- Ollama logs: `sudo journalctl -u ollama -f`

---

## 🎯 Next Steps After Completion

- [ ] Deploy frontend to Vercel/Netlify
- [ ] Point frontend to: `http://YOUR_GCP_IP:8000`
- [ ] Test end-to-end user flow
- [ ] Set up monitoring
- [ ] Add custom domain (optional)
- [ ] Enable HTTPS (optional)

---

## 🔧 Common Commands

**View logs:**
```bash
sudo journalctl -u defi-backend -f
sudo journalctl -u ollama -f
```

**Restart services:**
```bash
sudo systemctl restart defi-backend
sudo systemctl restart ollama
```

**Update code:**
```bash
cd ~/defi-project
git pull
sudo systemctl restart defi-backend
```

**Refresh vector store:**
```bash
curl -X POST http://localhost:8000/api/v1/llm/refresh
```

---

## 📊 What You Have Now

| Component | Status | Location |
|-----------|--------|----------|
| Backend | ✅ | GCP e2-medium |
| Database | ✅ | Same GCP |
| TinyLlama | ✅ | Same GCP |
| Vector Store | ✅ | Same GCP |
| Auto-restart | ✅ | systemd |
| External Access | ✅ | HTTP |

**Monthly Cost:** ~$24 (covered by your $300 credit = 12 months free!)

---

## 🆘 Troubleshooting

### If backend fails to start:
```bash
sudo journalctl -u defi-backend -n 50
```

### If Ollama fails:
```bash
curl http://localhost:11434
sudo systemctl restart ollama
```

### If vector store initialization fails:
```bash
# Check database
sudo -u postgres psql -d defi_risk_assessment -U defi_user

# Check models
ollama list

# Try again
curl -X POST http://localhost:8000/api/v1/llm/initialize
```

---

**Total Time: ~2 hours**  
**Result: Fully working LLM system on GCP!** 🎉

