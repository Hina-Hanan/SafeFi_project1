# Email Alerts Setup Guide

## Quick Fix for Email Alert Warning

The warning "Email alerts are currently disabled. Please configure SMTP settings in the backend" appears because email configuration is not set up yet.

## Option 1: Disable Email Alerts (Recommended for Development)

**Fastest solution - removes the warning:**

1. Create `backend/.env` file (if it doesn't exist)
2. Add this line:
```bash
EMAIL_ALERTS_ENABLED=false
```

3. Restart your backend server

**Result:** Warning disappears, users can subscribe (data saved), but no emails sent.

---

## Option 2: Enable Email Alerts with Gmail

### Step 1: Get Gmail App Password

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not already on)
3. Search for "App passwords" or go to https://myaccount.google.com/apppasswords
4. Select:
   - App: **Mail**
   - Device: **Windows Computer** (or Other)
5. Click **Generate**
6. Copy the **16-character password** (looks like: `abcd efgh ijkl mnop`)

### Step 2: Configure Backend

Create or update `backend/.env`:

```bash
# Email Alert Configuration
EMAIL_ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
ALERT_SENDER_EMAIL=your-email@gmail.com
ALERT_SENDER_PASSWORD=abcdefghijklmnop
```

**Replace:**
- `your-email@gmail.com` with your actual Gmail address
- `abcdefghijklmnop` with the 16-character app password (remove spaces)

### Step 3: Restart Backend

```powershell
# Stop backend (Ctrl+C)
# Start again
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

### Step 4: Test

1. Go to dashboard → Email Alerts tab
2. Enter your email
3. Click "Subscribe to Alerts"
4. Check your email for alert notifications

---

## Option 3: Use Other Email Services

### Outlook/Hotmail

```bash
EMAIL_ALERTS_ENABLED=true
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
ALERT_SENDER_EMAIL=your-email@outlook.com
ALERT_SENDER_PASSWORD=your-password
```

### Custom SMTP Server

```bash
EMAIL_ALERTS_ENABLED=true
SMTP_HOST=mail.yourdomain.com
SMTP_PORT=587
ALERT_SENDER_EMAIL=alerts@yourdomain.com
ALERT_SENDER_PASSWORD=your-password
```

---

## Using the Template File

We've provided `backend/env.example` with all configuration options:

```powershell
# Copy template
cd backend
copy env.example .env

# Edit .env with your favorite editor
notepad .env
```

Update the email section and restart the backend.

---

## For GCP Deployment

When deploying to GCP, add the same environment variables to your `.env` file on the VM:

```bash
# On GCP VM
cd ~/main-project/backend
nano .env
# Add EMAIL_ALERTS_ENABLED and other settings
# Save: Ctrl+O, Enter, Ctrl+X

# Restart backend
sudo systemctl restart defi-backend
```

---

## Troubleshooting

### "Authentication failed" Error

**For Gmail:**
- Make sure you're using an **App Password**, not your regular password
- App Password must be 16 characters, no spaces
- 2-Step Verification must be enabled

### "Connection refused" Error

- Check SMTP_HOST and SMTP_PORT are correct
- Ensure firewall allows outbound port 587
- Try SMTP_PORT=465 (SSL) instead of 587 (TLS)

### Warning Still Shows

- Verify `.env` file is in `backend/` directory
- Restart backend server completely
- Check backend logs for errors: look for "Email alerts" in console

### Emails Not Sending

- Check `EMAIL_ALERTS_ENABLED=true` (not false)
- Verify `ALERT_SENDER_PASSWORD` is set
- Check spam/junk folder in recipient's email
- Look for error messages in backend console

---

## Security Notes

⚠️ **Important:**
- Never commit `.env` to git (it's in `.gitignore`)
- Use App Passwords, not regular passwords
- For production, use dedicated email service (SendGrid, AWS SES)
- Rotate passwords regularly

---

## Quick Commands Reference

```powershell
# Create .env from template
cd backend
copy env.example .env

# Edit .env
notepad .env

# Start backend
venv\Scripts\activate
uvicorn app.main:app --reload

# Check if .env is loaded
python -c "from app.core.config import settings; print(f'Email enabled: {settings.email_alerts_enabled}')"
```

---

## Production Recommendations

For production deployment:

1. **Use dedicated email service:**
   - SendGrid (free tier: 100 emails/day)
   - AWS SES (very cheap, $0.10 per 1000 emails)
   - Mailgun (free tier: 5000 emails/month)

2. **Set up email templates** with your branding
3. **Implement rate limiting** to prevent spam
4. **Add unsubscribe links** (already built-in)
5. **Monitor email delivery** rates

---

## Current Status

✅ Email alert system is built and ready
✅ Configuration structure is in place
✅ Frontend subscription form works
⏳ Waiting for SMTP credentials to activate

**Just add credentials to `.env` and restart!**

