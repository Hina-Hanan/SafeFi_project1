# Clean Up Local Ollama

## Step-by-Step Cleanup

### 1. Stop Running Services

**If Ollama is running:**
```bash
# Windows
taskkill /F /IM ollama.exe

# macOS/Linux
pkill ollama
```

**If ngrok is running:**
```bash
# Windows
taskkill /F /IM ngrok.exe

# macOS/Linux
pkill ngrok
```

### 2. Remove Ollama Models (Free up space)

```bash
# List all models
ollama list

# Remove Mistral (saves 4.1GB)
ollama rm mistral

# Remove embedding model
ollama rm nomic-embed-text

# Verify removal
ollama list
```

### 3. (Optional) Uninstall Ollama Completely

**Windows:**
```powershell
# Via Settings
# Settings → Apps → Ollama → Uninstall

# Or via command
winget uninstall Ollama.Ollama
```

**macOS:**
```bash
brew uninstall ollama
```

**Linux:**
```bash
sudo systemctl stop ollama
sudo systemctl disable ollama
sudo rm /usr/local/bin/ollama
sudo rm -rf /usr/share/ollama
```

### 4. (Optional) Uninstall ngrok

**Windows:**
```powershell
winget uninstall ngrok
```

**macOS:**
```bash
brew uninstall ngrok
```

**Linux:**
```bash
sudo rm /usr/local/bin/ngrok
```

### 5. Clean Up Backend Configuration

**Remove ngrok URL from .env:**

Open `backend/.env` and remove/comment out:
```bash
# OLLAMA_BASE_URL=https://abc123.ngrok.io  # Not needed anymore
```

---

## ✅ Cleanup Complete!

You've freed up ~5GB of space and removed unnecessary services.

**Next:** Deploy to GCP with TinyLlama!

