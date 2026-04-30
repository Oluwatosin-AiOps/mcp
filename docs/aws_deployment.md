# AWS — long-running public link

S3 is static storage only—run the app on a VM or container service.

App Runner: **new customers not accepted** from 2026‑04‑30 per AWS; use EC2 or ECS below.

| Option | HTTPS |
|--------|--------|
| EC2 + Docker Compose | Optional (Caddy / ALB) |
| ECS Fargate + ALB | Yes |
| Lightsail VM | Same idea as EC2 |

Process listens on `PORT` (`docker-compose.yml` sets 7860). Behind ALB targeting 8080, use `-e PORT=8080 -p 8080:8080`.

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

- **AMI:** Prefer **Ubuntu 22.04 LTS** or **24.04 LTS** (“Jammy” / “Noble”). **Avoid bleeding‑edge** Ubuntu images for demos if you can: mirrors sometimes omit **`docker-compose-plugin`** and **`docker.io`** until updates land (you may see codenames like **Resolute** on non‑LTS releases).
- **Instance type:** `t3.micro` / `t3a.micro` or `t3.small`.
- **Security group:** inbound **TCP 7860** (and **80/443** if you add HTTPS below).

### 2. Install Docker + Compose (works on LTS and most newer Ubuntu)

Do **not** rely only on `apt install docker.io docker-compose-plugin` on brand‑new Ubuntu releases — use **Docker’s installer** (ships **Docker Engine + Compose v2**):

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

### 3. Clone and run the app

```bash
git clone https://github.com/Oluwatosin-AiOps/mcp.git
cd mcp
cp .env.example .env
nano .env   # OPENAI_API_KEY, MCP_SERVER_URL
docker compose up -d --build
```

### 4. URL

Use **`http://<public-ip-or-dns>:7860`**. The app listens on **7860**, not **80** — browsing **`http://54.x.x.x/`** (no port) hits port 80 and usually shows **connection refused** even when the container is healthy.

**Security group:** inbound **TCP 7860** from your IP or `0.0.0.0/0` for a demo.

**Sanity checks on the instance:**

```bash
docker compose ps
docker compose logs -f --tail 50
curl -sSI http://127.0.0.1:7860/ | head -n5
```

If `curl` returns **200** locally but the browser fails, the problem is almost always **wrong URL (missing `:7860`)** or the **security group**.

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
