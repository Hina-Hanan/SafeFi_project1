# Batch Files Guide for Windows

## Quick Fix for Email Subscription Error

If you see: **"Email alerts are currently disabled. Please configure SMTP settings in the backend"**

### 🚀 **One-Click Fix:**

```powershell
cd backend
FIX_EMAIL_ERROR.bat
```

This will:
- ✅ Create `.env` file
- ✅ Add email configuration (disabled mode)
- ✅ Remove the error message
- ✅ Allow users to subscribe (data saved)
- ✅ No actual emails sent yet

Then **restart your backend** and the error disappears!

---

## Available Batch Files

### 1. **FIX_EMAIL_ERROR.bat** ⭐ RECOMMENDED
**Purpose:** Quick fix for email subscription error

**What it does:**
- Creates `.env` if missing
- Adds `EMAIL_ALERTS_ENABLED=false`
- Fixes the frontend error
- Preserves existing .env settings

**When to use:** When you see the email error message

**Run:**
```powershell
cd backend
FIX_EMAIL_ERROR.bat
```

---

### 2. **COMPLETE_ENV_SETUP.bat**
**Purpose:** Create complete `.env` configuration from scratch

**What it does:**
- Creates new `.env` with all settings
- Database, MLflow, LLM, Email configs
- Overwrites existing .env (asks first)

**When to use:** First-time setup or fresh start

**Run:**
```powershell
cd backend
COMPLETE_ENV_SETUP.bat
```

---

### 3. **SETUP_EMAIL_QUICK.bat**
**Purpose:** Configure email settings interactively

**What it does:**
- Guides you through email setup
- Can append to existing .env
- Options for new/existing .env

**When to use:** When setting up email for the first time

**Run:**
```powershell
cd backend
SETUP_EMAIL_QUICK.bat
```

---

## Step-by-Step: Fix Email Error

### Quick Method (30 seconds):

1. **Run the fix:**
   ```powershell
   cd backend
   FIX_EMAIL_ERROR.bat
   ```

2. **Restart backend:**
   - Press `Ctrl+C` in backend terminal
   - Run: `uvicorn app.main:app --reload`

3. **Refresh frontend:**
   - Open http://localhost:5173
   - Go to "📧 Email Alerts" tab
   - Error should be GONE! ✅

---

### Manual Method (if batch files don't work):

1. **Create `backend\.env` file:**
   - Copy `backend\env.example` to `backend\.env`
   - OR create new file named `.env` in `backend` folder

2. **Add this to `.env`:**
   ```bash
   EMAIL_ALERTS_ENABLED=false
   DATABASE_URL=postgresql+psycopg2://defi_user:usersafety@localhost:5432/defi_risk_assessment
   ```

3. **Restart backend**

---

## Understanding the Error

### Why does it happen?
The email subscription feature needs SMTP configuration. Without a `.env` file specifying `EMAIL_ALERTS_ENABLED=false`, the frontend shows a warning.

### Why disable emails?
- ✅ **For testing:** Users can subscribe, data is saved
- ✅ **No spam:** No actual emails sent yet
- ✅ **Enable later:** When you're ready with Gmail App Password

### Does subscription still work?
**YES!** Users can:
- ✅ Enter email and subscribe
- ✅ Set risk thresholds
- ✅ Data is saved in database
- ❌ Emails not sent (until you enable SMTP)

---

## Enable Real Email Alerts (Optional)

### Step 1: Get Gmail App Password

1. Go to: https://myaccount.google.com/security
2. Enable **2-Step Verification**
3. Search "App passwords" or go to: https://myaccount.google.com/apppasswords
4. Select **Mail** and **Windows Computer**
5. Click **Generate**
6. Copy the 16-character password

### Step 2: Edit `.env`

Open `backend\.env` and update:

```bash
EMAIL_ALERTS_ENABLED=true
ALERT_SENDER_EMAIL=your-email@gmail.com
ALERT_SENDER_PASSWORD=your-16-char-app-password
```

### Step 3: Restart Backend

```powershell
# Stop backend (Ctrl+C)
# Start again
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

Now real emails will be sent! 📧

---

## Troubleshooting

### .env file not created?

**Check:**
- Are you in `backend` folder?
- Run as Administrator if permission issues
- Try manual method above

### Error still shows after fix?

**Solutions:**
1. Completely stop backend (`Ctrl+C`)
2. Check `.env` exists in `backend` folder
3. Verify it contains `EMAIL_ALERTS_ENABLED=false`
4. Start backend fresh
5. Hard refresh frontend (`Ctrl+Shift+R`)

### Can't find .env file?

**Windows hides dot files by default:**
1. Open File Explorer
2. View → Show → Hidden items
3. OR use PowerShell: `ls -Force` in backend folder

### Want to use different email provider?

Edit `.env`:
```bash
# Outlook/Hotmail
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587

# Custom SMTP
SMTP_HOST=mail.yourdomain.com
SMTP_PORT=587
```

---

## For GCP Deployment

These batch files are **only for local Windows development**. 

On GCP (Linux), you'll create `.env` manually:
```bash
# On GCP VM
nano ~/main-project/backend/.env
# Add EMAIL_ALERTS_ENABLED=false
# Save: Ctrl+O, Enter, Ctrl+X
```

---

## Summary

### To fix email subscription error:

1. **Run:** `backend\FIX_EMAIL_ERROR.bat`
2. **Restart:** Backend server
3. **Done:** Error disappears ✅

### Current Status:
- ✅ Email subscription form works
- ✅ Data is saved in database
- ✅ No error messages
- ⏳ Real email sending (enable when ready)

---

## Quick Commands Reference

```powershell
# Fix email error (FASTEST)
cd backend
FIX_EMAIL_ERROR.bat

# Complete fresh setup
cd backend
COMPLETE_ENV_SETUP.bat

# Interactive email setup
cd backend
SETUP_EMAIL_QUICK.bat

# Check if .env exists
cd backend
dir .env

# View .env contents
cd backend
type .env

# Start backend after fix
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

---

**Need help?** Check `EMAIL_ALERTS_SETUP.md` for detailed documentation!

