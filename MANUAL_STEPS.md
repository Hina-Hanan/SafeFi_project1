# ⚠️ Manual Steps Required

## Frontend Environment File

**Important:** You need to manually create the frontend production environment file.

### Step: Create `.env.production` file

**Location:** `frontend/.env.production`

**On your local machine:**

```bash
# Navigate to frontend directory
cd frontend

# Create .env.production file
# Use any text editor (VS Code, Notepad, etc.)
```

**Add this content:**

```bash
# Production Environment Configuration
# Replace YOUR_GCP_IP with your actual GCP External IP

VITE_API_BASE_URL=http://YOUR_GCP_IP:8000

# Example (use your actual IP):
# VITE_API_BASE_URL=http://34.123.45.67:8000
```

**Replace `YOUR_GCP_IP` with the External IP from your GCP instance!**

### How to Find Your GCP IP

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Navigate to **Compute Engine** → **VM Instances**
3. Find your `defi-backend` instance
4. Copy the **External IP** (e.g., `34.123.45.67`)
5. Use that IP in the `.env.production` file

### Example

If your GCP External IP is `34.123.45.67`, your file should be:

```bash
VITE_API_BASE_URL=http://34.123.45.67:8000
```

---

## Why Manually?

The `.env.production` file couldn't be created automatically because:
- `.env` files are typically in `.gitignore`
- This prevents accidental commit of sensitive data
- You need to create it manually with your specific IP

---

## After Creating This File

1. **Commit and push:**
   ```bash
   git add .env.production
   git commit -m "Add production environment config"
   git push origin main
   ```

2. **Proceed with Vercel deployment** (Step 3.2 in START_HERE.md)

---

**That's it!** This is the only manual file creation needed.

