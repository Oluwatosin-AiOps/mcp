#!/usr/bin/env bash
# EC2 user-data helper: Docker via get.docker.com, shallow clone. Edit /opt/meridian-mcp/.env then docker compose up -d --build.
set -euxo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y ca-certificates curl git
curl -fsSL https://get.docker.com | sh
systemctl enable --now docker
install -d /opt
if [[ ! -d /opt/meridian-mcp/.git ]]; then
  git clone --depth 1 https://github.com/Oluwatosin-AiOps/mcp.git /opt/meridian-mcp
fi
cd /opt/meridian-mcp
if [[ ! -f .env ]]; then
  cp .env.example .env
  chmod 600 .env
  echo "EDIT /opt/meridian-mcp/.env (OPENAI_API_KEY, MCP_SERVER_URL) then run:"
  echo "  cd /opt/meridian-mcp && sudo docker compose up -d --build"
fi
