#!/usr/bin/env bash
set -euo pipefail

# Update system
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Install Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"

# Install Ollama for local LLM
curl -fsSL https://ollama.ai/install.sh | sh

# Pull default model (mistral)
ollama pull mistral &
# This runs in background; docker compose will retry connections to http://localhost:11434

mkdir -p ~/support-copilot/deploy/nginx

echo "EC2 setup complete. Re-login for docker group membership to apply."
echo "Ollama is installing mistral model in the background..."
echo "Verify Ollama is ready with: curl http://localhost:11434/api/tags"
