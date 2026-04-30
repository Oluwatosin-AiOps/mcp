# Meridian MCP customer support

Gradio UI + GPT-4o-mini tool-calling against Meridian’s MCP server (Streamable HTTP). Inventory and orders come from tools, not free‑text guesses.

## Deployment (EC2)

This project is run on **AWS EC2** (not Hugging Face Spaces—Spaces builds were unreliable for this setup). Standard pattern:

1. **Ubuntu 22.04 or 24.04 LTS** instance; security group allows **inbound TCP 7860** (and **80/443** if you terminate TLS on the box).
2. Install Docker: `curl -fsSL https://get.docker.com | sudo sh` (on newer Ubuntu, `apt install docker-compose-plugin` alone often fails).
3. Clone the repo, `cp .env.example .env`, set `OPENAI_API_KEY` and `MCP_SERVER_URL`.
4. `docker compose up -d --build` — open **`http://<your-public-ip>:7860`** (Gradio is **not** on port 80; `http://ip/` alone will show connection refused).

Details: **`docs/aws_deployment.md`**, **`docker-compose.yml`**, **`scripts/ec2_diagnose.sh`** (run on the instance), **`scripts/ec2_bootstrap_ubuntu.sh`**.

For **HTTPS**, use Caddy or an ALB + ACM (see the same doc). **ECS Fargate + ALB** is an alternative if you already use ECR.

## Architecture

![Architecture](docs/arch-diagram.png)

| Layer | Code |
|-------|------|
| UI | `app/ui.py`, `app.py` |
| Agent | `app/agent.py` |
| Guardrails | `app/guardrails.py` |
| Auth | `app/auth_session.py` |
| MCP | `app/mcp_client.py` |
| Config | `app/config.py` |

The diagram mentions tracing stacks (e.g. Langfuse); this repo does not wire those—only tests, smoke scripts, and logs.

## Decisions

- OpenAI SDK + official MCP Python SDK (no LangChain).
- Default model `gpt-4o-mini` (`MODEL_NAME`).
- uv dev (`pyproject.toml` / `uv.lock`); `requirements.txt` from `uv export` for pip and container builds.
- PIN gating and customer scope in code (`auth_session.py`), aligned with `docs/prompt_iterations.md`.
- Live MCP tests behind `MERIDIAN_*` env vars (`docs/test_results.md`).

## Setup

1. [uv](https://docs.astral.sh/uv/installation/), Python 3.12 (`.python-version`).
2. `uv sync`
3. Copy `.env.example` → `.env`; set `OPENAI_API_KEY`, `MCP_SERVER_URL`. Do not commit `.env`.
4. Without uv: `pip install -r requirements.txt` (Python ≥ 3.10).

## Run

```bash
uv run python app.py                      # Gradio
uv run python app.py --print-config       # Print MCP URL + model
uv run python app.py "Your question"      # One CLI turn
uv run pytest
uv run pytest -m "not integration" -q     # Skip integration markers
```

Smoke scripts (MCP only): `scripts/discover_tools.py`, `smoke_product_tools.py`, `smoke_order_history.py`, `smoke_order_placement.py` (placement creates orders—use only on the MCP endpoint you intend).

## Docs

| Path | Content |
|------|---------|
| `docs/problem_framing.md` | Scope and success criteria |
| `docs/mcp_tools.md` | Tool list |
| `docs/guardrails.md` | Input/output filters |
| `docs/test_results.md` | Pytest layout |
| `docs/prompt_iterations.md` | System prompt versions |
| `docs/aws_deployment.md` | EC2, HTTPS, ECS |
| `docs/project_structure.md` | Tree |

## Requirements export

```bash
uv export --format requirements-txt --no-hashes --no-annotate > requirements.txt
```
