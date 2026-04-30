# AWS EC2 deployment

The Meridian chatbot runs on **AWS EC2** with **Docker Compose**. The container builds from the repo **`Dockerfile`** and listens on **7860** (`docker-compose.yml`, `GRADIO_SERVER_NAME=0.0.0.0`).

---

## 1. Launch EC2

- **AMI:** **Ubuntu 22.04 LTS** or **24.04 LTS** (“Jammy” / “Noble”). On some non‑LTS images, default apt mirrors may not yet ship a working **`docker-compose-plugin`**; the install script below avoids that.
- **Instance type:** `t3.micro` / `t3a.micro` or `t3.small`.
- **Security group:** inbound **TCP 7860** (browser traffic to Gradio).

---

## 2. Install Docker Engine + Compose v2

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
curl -fsSL https://get.docker.com | sudo sh
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu
```

Log out and SSH back in so group **`docker`** applies, **or** prefix **`docker`** with **`sudo`** below.

Verify:

```bash
docker --version
docker compose version
```

---

## 3. Clone and run

```bash
git clone https://github.com/Oluwatosin-AiOps/mcp.git
cd mcp
cp .env.example .env
nano .env   # OPENAI_API_KEY, MCP_SERVER_URL
docker compose up -d --build
```

---

## 4. Public URL

Open **`http://<public-ip>:7860`**. The app listens on **7860**, not **80** — **`http://<ip>/`** (no port) hits port 80 and usually shows **connection refused** even when the container is healthy.

**Sanity checks on the instance:**

```bash
docker compose ps
docker compose logs -f --tail 50
curl -sSI http://127.0.0.1:7860/ | head -n5
```

If `curl` works on the instance but the browser does not, fix the **security group** (TCP **7860**) or **UFW** on Ubuntu:

```bash
sudo ufw status verbose
sudo ufw allow 7860/tcp && sudo ufw reload   # only if ufw is active
```

---

## 5. Pull updates and redeploy

```bash
cd ~/mcp   # your clone path
git pull
bash scripts/ec2_diagnose.sh
docker compose down && docker compose up -d --build
```

---

## Secrets

Do not commit API keys. On the instance, keep **`.env`** readable only by your user (e.g. **`chmod 600 .env`**).

---

## Cost

Stop the EC2 instance when you are not running the demo to avoid ongoing compute charges.
