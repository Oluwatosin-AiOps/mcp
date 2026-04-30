#!/usr/bin/env bash
# Run on the EC2 host (not inside the container). From repo root: bash scripts/ec2_diagnose.sh
set -euo pipefail
echo "=== public IPv4 (compare with browser URL) ==="
curl -fsS --max-time 3 https://checkip.amazonaws.com/ || true
echo ""
echo "=== docker containers ==="
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || true
echo ""
echo "=== compose (if cwd has docker-compose.yml, pass dir): ${PWD} ==="
if [[ -f docker-compose.yml ]]; then
  docker compose ps 2>/dev/null || true
  echo "--- last 80 log lines ---"
  docker compose logs --tail 80 2>/dev/null || true
else
  echo "(no docker-compose.yml here — cd to your mcp clone first)"
fi
echo ""
echo "=== listeners on 7860 ==="
sudo ss -tlnp | grep -E ':7860\b' || echo "nothing listening on 7860"
echo ""
echo "=== curl loopback (expect HTTP headers, not connection refused) ==="
curl -sSI --max-time 5 http://127.0.0.1:7860/ | head -n 8 || echo "curl failed — app not listening"
echo ""
echo "=== ufw (if inactive, empty rules — OK) ==="
sudo ufw status verbose 2>/dev/null || echo "ufw not installed"
echo ""
echo "Hints: browser URL must be http://THIS_HOST_IP:7860 (not port 80)."
echo "EC2 security group must allow inbound TCP 7860."
echo "If ufw is active: sudo ufw allow 7860/tcp && sudo ufw reload"
