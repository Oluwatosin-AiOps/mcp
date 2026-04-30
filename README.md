---
title: Meridian MCP Customer Support
emoji: 🛒
colorFrom: blue
colorTo: gray
sdk: gradio
sdk_version: 6.13.0
python_version: "3.12"
app_file: app.py
pinned: false
short_description: GPT-4o-mini + MCP customer support chatbot.
tags:
  - gradio
  - mcp
  - openai
---

# Meridian MCP customer support

Gradio UI + GPT-4o-mini tool-calling against Meridian’s MCP server (Streamable HTTP). Inventory and orders come from tools, not free‑text guesses.

The YAML header is for [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces-config-reference).

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
- uv dev (`pyproject.toml` / `uv.lock`); `requirements.txt` from `uv export` for pip / Spaces.
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

## Hugging Face Spaces

Create a Gradio Space from this repo; set secrets `OPENAI_API_KEY`, `MCP_SERVER_URL`, optional `MODEL_NAME`. First build can take 10–20 minutes on free CPU. See Space **Logs** if stuck. `PORT` is handled in `app/ui.py`.

## AWS

Not on S3—needs a VM or container service. App Runner closed to new accounts from 2026‑04‑30. Use EC2 + `docker compose` (`docs/aws_deployment.md`, `docker-compose.yml`) or ECS Fargate + ALB. On newer Ubuntu, install Docker with `curl -fsSL https://get.docker.com | sudo sh`, not only `apt install docker-compose-plugin`.

## Docs

| Path | Content |
|------|---------|
| `docs/problem_framing.md` | Scope and success criteria |
| `docs/mcp_tools.md` | Tool list |
| `docs/guardrails.md` | Input/output filters |
| `docs/test_results.md` | Pytest layout |
| `docs/prompt_iterations.md` | System prompt versions |
| `docs/aws_deployment.md` | EC2 / ECS |
| `docs/project_structure.md` | Tree |

## Requirements export

```bash
uv export --format requirements-txt --no-hashes --no-annotate > requirements.txt
```
