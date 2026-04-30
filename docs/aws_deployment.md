# AWS — long-running public link (EC2 or App Runner)

S3 cannot run this app; you need **compute**. The two fastest **long-lived** options are:

| Option | HTTPS | Typical time (first deploy) |
|--------|-------|-----------------------------|
| **A. App Runner + ECR** | Yes (`*.awsapprunner.com`) | ~20–40 min |
| **B. EC2 + Docker Compose** | HTTP on `:7860` unless you add nginx/ALB | ~15–25 min |

Your container listens on the **`PORT`** environment variable (defaults to **7860** locally). **AWS App Runner** sets **`PORT` to 8080** by default — the app already reads `PORT`, so no code change is needed.

---

## Shared: build the image locally

From the repo root (Docker Desktop or Linux with Docker):

```bash
docker build -t meridian-mcp:latest .
```

---

## A) App Runner + ECR (recommended for a stable **HTTPS** URL)

### 1. ECR repository and push

Replace `REGION` (e.g. `us-east-1`) and run:

```bash
export AWS_REGION=us-east-1
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ECR_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/meridian-mcp"

aws ecr create-repository --repository-name meridian-mcp --region "$AWS_REGION" 2>/dev/null || true
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

docker tag meridian-mcp:latest "${ECR_URI}:latest"
docker push "${ECR_URI}:latest"
```

### 2. Create the App Runner service (console — least error-prone)

1. AWS Console → **App Runner** → **Create service**.
2. **Repository type:** Container registry → **Amazon ECR**.
3. **Image:** pick `meridian-mcp:latest` from the repo you pushed.
4. **Deployment settings:** automatic is fine for a demo.
5. **Service settings → Port:** **8080** (App Runner default; it will set `PORT=8080` for your process).
6. **Environment variables** (or “Secrets” where available):
   - `OPENAI_API_KEY` — store as **secret**.
   - `MCP_SERVER_URL` — assessment MCP URL.
   - `MODEL_NAME` — optional, default `gpt-4o-mini`.
7. Create the service and wait until status is **Running**.

You get a URL like **`https://xxxxxxxxxx.us-east-1.awsapprunner.com`** — that is your long-running link.

**Docs:** [App Runner](https://docs.aws.amazon.com/apprunner/latest/dg/what-is-apprunner.html), [ECR push](https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html).

---

## B) EC2 + Docker Compose (fast **HTTP** link)

### 1. Launch EC2

- **AMI:** Ubuntu 22.04 LTS (or 24.04).
- **Instance type:** `t3.micro` / `t3a.micro` (Free Tier eligible in some accounts) or small `t3.small`.
- **Storage:** 8–16 GiB gp3 is enough.
- **Security group:** inbound **TCP 7860** from `0.0.0.0/0` for a public demo (narrow to your IP later).

### 2. Install Docker and the app

SSH in as `ubuntu`, then either:

**Option B1 — clone this repo**

```bash
sudo apt-get update && sudo apt-get install -y docker.io docker-compose-plugin git
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu
# log out and back in so `docker` works without sudo, or use sudo for docker below

git clone https://github.com/Oluwatosin-AiOps/mcp.git
cd mcp
cp .env.example .env
nano .env   # set OPENAI_API_KEY and MCP_SERVER_URL
docker compose up -d --build
```

**Option B2 — bootstrap script** (same idea; see `scripts/ec2_bootstrap_ubuntu.sh`).

### 3. Open the app

Browser: **`http://<EC2-public-ipv4-dns>:7860`**

Use an **Elastic IP** if you want the address to stay fixed across stop/start.

### HTTPS on EC2 (optional)

Put **Application Load Balancer + ACM certificate** in front, or **Caddy/nginx + Let’s Encrypt** on the instance. App Runner avoids this work.

---

## Secrets

Never commit **OpenAI** or **AWS** keys. Use App Runner secrets / SSM Parameter Store / EC2 instance user data **only** for non-secret bootstrap — put API keys in **`.env` on the server** with `chmod 600` or inject via **Docker `--env-file`** from a root-only file.

---

## Cost

Always-on **EC2** or **App Runner** incurs charges. Stop the EC2 instance or delete the App Runner service when you are done demoing.
