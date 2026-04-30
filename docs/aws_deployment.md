# AWS deployment (when Hugging Face Spaces is not used)

## Why not S3 alone?

**Amazon S3** stores objects (files). It does **not** execute Python or host a long‑lived Gradio server. This project needs a **process** that stays up, talks to **OpenAI**, and opens **MCP (HTTP)** sessions—so you need **compute** (VM or container), not static hosting.

You *can* put a **static marketing page** on S3 and link out to your real app URL; that is optional polish, not a replacement for the chat backend.

## Practical options that give you a **link**

| Option | Complexity | URL |
|--------|------------|-----|
| **EC2** (small instance) | Low–medium | `http://<public-ip>:7860` or put **ALB + HTTPS** in front |
| **App Runner** | Medium | AWS gives an `*.awsapprunner.com` HTTPS URL |
| **ECS Fargate** + ALB | Higher | Your domain or ALB DNS |

Fastest path for a demo: **EC2 + Docker** (or install Python on the box) and open **security group** port **7860** (or **80** behind nginx).

## Docker (repo root)

```bash
docker build -t meridian-mcp .
docker run --rm -p 7860:7860 \
  -e OPENAI_API_KEY="sk-..." \
  -e MCP_SERVER_URL="https://.../mcp" \
  -e MODEL_NAME="gpt-4o-mini" \
  meridian-mcp
```

Then open `http://localhost:7860` locally, or `http://<EC2-public-dns>:7860` if the instance security group allows inbound **7860** from your IP (or `0.0.0.0/0` for a short demo—tighten later).

**Never commit** AWS keys or OpenAI keys; pass them only as environment variables or AWS Secrets Manager / Parameter Store and inject at runtime.

## App Runner (sketch)

1. Push the image to **Amazon ECR**.
2. Create an **App Runner** service from that image.
3. Configure **runtime environment variables**: `OPENAI_API_KEY`, `MCP_SERVER_URL`, `MODEL_NAME` (use Secrets integration where offered).
4. Use the **default HTTPS URL** App Runner provides.

Exact clicks change in the AWS console; follow the “Deploy from ECR” wizard.

## HTTPS

- **App Runner / ALB**: HTTPS is built-in or straightforward.
- **Bare EC2 on :7860**: usually **HTTP** only; for HTTPS put **nginx + Let’s Encrypt** or an **ALB** in front.

## Cost note

Always-on demo instances incur charges; use the smallest shape and stop the instance when not demoing.
