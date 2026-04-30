# AWS — long-running public link

S3 cannot run this app; you need **compute**.

> **App Runner (April 30, 2026):** AWS is **no longer onboarding new App Runner customers**. If you do not already have App Runner, use the paths below instead. See [AWS announcement](https://aws.amazon.com/apprunner/) / current AWS docs for your account.

| Option | HTTPS | Notes |
|--------|-------|--------|
| **EC2 + Docker Compose** | Optional (see below) | Fastest path; **`docker-compose.yml`** in repo |
| **ECS Fargate + ALB** | Yes | Good if you already pushed to **ECR** and want managed containers |
| **Lightsail** (VM + Docker) | Optional | Same pattern as EC2, simpler console / fixed pricing |

Your app listens on **`PORT`** (default **7860** in `docker-compose.yml`). For plain **`docker run`** without compose, set **`-e PORT=8080 -p 8080:8080`** if you front it with a proxy expecting 8080.

---

## Shared: build the image locally

```bash
docker build -t meridian-mcp:latest .
```

**ECR push** (optional — for ECS or sharing an image):

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

---

## A) EC2 + Docker Compose (recommended default)

### 1. Launch EC2

- **AMI:** Ubuntu 22.04 or 24.04 LTS.
- **Instance type:** `t3.micro` / `t3a.micro` or `t3.small`.
- **Security group:** inbound **TCP 7860** (and **80/443** if you add HTTPS below).

### 2. Install and run

```bash
sudo apt-get update && sudo apt-get install -y docker.io docker-compose-plugin git
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu
# re-login for docker group, or use sudo docker …

git clone https://github.com/Oluwatosin-AiOps/mcp.git
cd mcp
cp .env.example .env
nano .env   # OPENAI_API_KEY, MCP_SERVER_URL
docker compose up -d --build
```

### 3. URL

**`http://<EC2-public-dns>:7860`** — attach an **Elastic IP** if you want a stable IPv4.

### Optional: HTTPS on EC2 with **Caddy** (free TLS, you need a **domain**)

1. Point **`chat.yourdomain.com`** DNS **A record** to the instance public IP.
2. Open security group **80** and **443**.
3. On the instance, add a `Caddyfile` next to the repo:

```text
chat.yourdomain.com {
    reverse_proxy localhost:7860
}
```

4. Run Caddy (example one-liner):

```bash
docker run -d --name caddy --restart unless-stopped \
  -p 80:80 -p 443:443 \
  -v $PWD/Caddyfile:/etc/caddy/Caddyfile:ro \
  caddy:2-alpine
```

Caddy obtains Let’s Encrypt certificates automatically. Your app stays on **7860**; only Caddy faces the internet.

**Alternative:** **Application Load Balancer + ACM** certificate — more AWS-native, more clicks.

---

## B) ECS Fargate + Application Load Balancer (HTTPS, no App Runner)

High level (exact console steps change over time):

1. Push image to **ECR** (commands above).
2. **ECS** → create cluster → **Fargate** task definition: container port **8080**, set env vars / secrets for `OPENAI_API_KEY`, `MCP_SERVER_URL`, `MODEL_NAME`, and **`PORT=8080`**.
3. Create a **service** with an **Application Load Balancer**, listener **HTTPS (443)** with **ACM** certificate, target group → container port **8080**.
4. Use the ALB DNS name as your public URL.

Docs: [ECS Fargate getting started](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/getting-started-fargate.html), [ALB with ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-load-balancing.html).

---

## Secrets

Never commit API keys. On EC2, keep **`.env`** mode `600`. On ECS, use **Secrets Manager** or task definition secrets.

---

## Cost

Stop the EC2 instance or scale ECS to zero when not demoing (Fargate tasks bill while running).
