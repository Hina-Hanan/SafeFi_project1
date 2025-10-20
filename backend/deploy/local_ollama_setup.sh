#!/bin/bash
# Local Ollama Setup for Hybrid Deployment
# Run this on your local machine

set -e

echo "=========================================="
echo "Local Ollama Setup for Hybrid Deployment"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo -e "${RED}Unsupported OS. Please install Ollama manually.${NC}"
    exit 1
fi

echo -e "${GREEN}[1/5] Checking Ollama installation...${NC}"
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Installing..."
    
    if [ "$OS" == "linux" ]; then
        curl -fsSL https://ollama.ai/install.sh | sh
    elif [ "$OS" == "macos" ]; then
        brew install ollama
    fi
else
    echo "Ollama already installed"
fi

echo -e "${GREEN}[2/5] Pulling Mistral model...${NC}"
ollama pull mistral

echo -e "${GREEN}[3/5] Pulling embedding model...${NC}"
ollama pull nomic-embed-text

echo ""
echo "=========================================="
echo "Choose Connection Method"
echo "=========================================="
echo ""
echo "1) Tailscale VPN (Recommended - Most Secure)"
echo "2) ngrok (Easy - Good for Testing)"
echo "3) Direct Expose (Advanced - Requires Port Forwarding)"
echo ""
read -p "Enter choice (1-3): " CONNECTION_METHOD

case $CONNECTION_METHOD in
    1)
        echo -e "${GREEN}[4/5] Setting up Tailscale...${NC}"
        
        if ! command -v tailscale &> /dev/null; then
            echo "Installing Tailscale..."
            
            if [ "$OS" == "linux" ]; then
                curl -fsSL https://tailscale.com/install.sh | sh
            elif [ "$OS" == "macos" ]; then
                brew install tailscale
            fi
        fi
        
        echo "Starting Tailscale..."
        sudo tailscale up
        
        TAILSCALE_IP=$(tailscale ip -4)
        echo ""
        echo -e "${GREEN}Tailscale IP: $TAILSCALE_IP${NC}"
        echo ""
        
        echo -e "${GREEN}[5/5] Starting Ollama...${NC}"
        echo "Ollama will listen on all interfaces for Tailscale access"
        
        # Add to shell profile
        if [ "$OS" == "linux" ]; then
            echo 'export OLLAMA_HOST=0.0.0.0' >> ~/.bashrc
            export OLLAMA_HOST=0.0.0.0
        elif [ "$OS" == "macos" ]; then
            echo 'export OLLAMA_HOST=0.0.0.0' >> ~/.zshrc
            export OLLAMA_HOST=0.0.0.0
        fi
        
        echo ""
        echo "=========================================="
        echo -e "${GREEN}Setup Complete!${NC}"
        echo "=========================================="
        echo ""
        echo "Tailscale IP: $TAILSCALE_IP"
        echo "Ollama URL: http://$TAILSCALE_IP:11434"
        echo ""
        echo "Next Steps:"
        echo "1. Install Tailscale on your GCP instance"
        echo "2. Use this URL in GCP .env: OLLAMA_BASE_URL=http://$TAILSCALE_IP:11434"
        echo "3. Start Ollama: ollama serve"
        echo ""
        ;;
        
    2)
        echo -e "${GREEN}[4/5] Setting up ngrok...${NC}"
        
        if ! command -v ngrok &> /dev/null; then
            echo "Installing ngrok..."
            
            if [ "$OS" == "linux" ]; then
                curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
                    sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
                    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
                    sudo tee /etc/apt/sources.list.d/ngrok.list && \
                    sudo apt update && sudo apt install ngrok
            elif [ "$OS" == "macos" ]; then
                brew install ngrok/ngrok/ngrok
            fi
        fi
        
        echo ""
        echo "ngrok requires a free account."
        echo "1. Sign up at: https://dashboard.ngrok.com/signup"
        echo "2. Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken"
        echo ""
        read -p "Enter your ngrok authtoken: " NGROK_TOKEN
        ngrok authtoken $NGROK_TOKEN
        
        echo -e "${GREEN}[5/5] Starting services...${NC}"
        
        # Start Ollama in background
        ollama serve &
        OLLAMA_PID=$!
        
        sleep 3
        
        # Start ngrok in background
        ngrok http 11434 > /dev/null &
        NGROK_PID=$!
        
        sleep 5
        
        # Get ngrok URL
        NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*')
        
        echo ""
        echo "=========================================="
        echo -e "${GREEN}Setup Complete!${NC}"
        echo "=========================================="
        echo ""
        echo "ngrok URL: $NGROK_URL"
        echo ""
        echo "Next Steps:"
        echo "1. Keep this terminal running (ngrok and Ollama)"
        echo "2. Use this URL in GCP .env: OLLAMA_BASE_URL=$NGROK_URL"
        echo ""
        echo -e "${YELLOW}NOTE: Free ngrok URLs change on restart. Consider Tailscale for static IPs.${NC}"
        echo ""
        echo "To stop: kill $OLLAMA_PID $NGROK_PID"
        echo ""
        
        # Keep running
        wait
        ;;
        
    3)
        echo -e "${GREEN}[4/5] Direct Expose Setup${NC}"
        
        # Get local IP
        if [ "$OS" == "linux" ]; then
            LOCAL_IP=$(hostname -I | awk '{print $1}')
        elif [ "$OS" == "macos" ]; then
            LOCAL_IP=$(ipconfig getifaddr en0)
        fi
        
        # Get public IP
        PUBLIC_IP=$(curl -s ifconfig.me)
        
        echo ""
        echo "Local IP: $LOCAL_IP"
        echo "Public IP: $PUBLIC_IP"
        echo ""
        echo -e "${YELLOW}WARNING: You need to configure port forwarding on your router!${NC}"
        echo ""
        echo "Steps:"
        echo "1. Log into your router admin panel"
        echo "2. Forward external port 11434 to $LOCAL_IP:11434"
        echo "3. Test from outside: curl http://$PUBLIC_IP:11434"
        echo ""
        
        # Add to shell profile
        if [ "$OS" == "linux" ]; then
            echo 'export OLLAMA_HOST=0.0.0.0' >> ~/.bashrc
            export OLLAMA_HOST=0.0.0.0
        elif [ "$OS" == "macos" ]; then
            echo 'export OLLAMA_HOST=0.0.0.0' >> ~/.zshrc
            export OLLAMA_HOST=0.0.0.0
        fi
        
        echo -e "${GREEN}[5/5] Starting Ollama...${NC}"
        
        echo ""
        echo "=========================================="
        echo -e "${GREEN}Setup Complete!${NC}"
        echo "=========================================="
        echo ""
        echo "Ollama URL: http://$PUBLIC_IP:11434"
        echo ""
        echo "Next Steps:"
        echo "1. Configure port forwarding on your router"
        echo "2. Test: curl http://$PUBLIC_IP:11434"
        echo "3. Use this URL in GCP .env: OLLAMA_BASE_URL=http://$PUBLIC_IP:11434"
        echo "4. Start Ollama: ollama serve"
        echo ""
        ;;
        
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac


