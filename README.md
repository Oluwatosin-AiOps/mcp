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
short_description: GPT-4o-mini + MCP (Meridian order server) customer support chatbot.
tags:
  - gradio
  - mcp
  - openai
---

# Meridian Electronics — MCP Customer Support Chatbot

Prototype chatbot that uses the official MCP Python SDK and OpenAI tool calling to reach Meridian’s order MCP server.

The **YAML block above** is read by [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces-config-reference) (Gradio SDK, `app.py` entrypoint). GitHub will simply show it at the top of this file; that is normal for dual-purpose repos.

## Setup (Stage 0)

1. Install [uv](https://docs.astral.sh/uv/installation/). The repo pins **Python 3.12** in `.python-version`; uv will download that runtime if it is not installed yet.

2. Install dependencies from the lockfile:

   ```bash
   uv sync
   ```

   uv keeps a project virtual environment under `.venv`. You do not need to activate it if you run everything through `uv run` (below).

3. **Without uv:** use Python **3.10+** and `pip install -r requirements.txt`. That file is exported from `uv.lock` so Hugging Face Spaces and plain pip stay reproducible.

4. **Environment:** copy `.env.example` to `.env` and set `OPENAI_API_KEY`. Never commit `.env`.

5. **GitHub repo:** create an empty repository on GitHub (e.g. under your user or org), then:

   ```bash
   git remote add origin https://github.com/<your-account>/<your-repo>.git
   git branch -M main
   git push -u origin main
   ```

## Project layout (Stage 3)

| Path | Role |
|------|------|
| `app/config.py` | Load `.env`, validate `MCP_SERVER_URL`, `OPENAI_API_KEY`, `MODEL_NAME` |
| `app/mcp_client.py` | Tool specs for OpenAI, ``tools/call``, format results for the model |
| `app/agent.py` | GPT-4o-mini tool loop over MCP (Streamable HTTP) |
| `app/guardrails.py` | Input validation, injection/privilege refusal, secret-pattern filter, reply clipping |
| `app/auth_session.py` | PIN verification gates order/account MCP tools per turn |
| `app/ui.py` | Gradio chat UI |
| `tests/` | pytest |
| `docs/` | Problem framing, MCP notes, **`guardrails.md`**, **`test_results.md`**, **`prompt_iterations.md`**, prompt log |
| `scripts/` | Standalone tool discovery (Stage 5) |
| `app.py` | Space/local entrypoint |

See `docs/project_structure.md` for the tree and import boundaries.

## Commands

```bash
uv run pytest
uv run pytest -m "not integration"   # same fast suite when integration tests are marked
uv run python app.py                 # Gradio UI (opens browser locally; binds 0.0.0.0:7860 by default)
uv run python app.py --print-config   # print MCP URL + model, then exit
uv run python app.py "Search for wireless keyboards and summarize."   # one-shot CLI agent turn
uv run python scripts/discover_tools.py
uv run python scripts/smoke_product_tools.py
uv run python scripts/smoke_order_history.py
uv run python scripts/smoke_order_placement.py
```

**`app.py`:** no arguments → **Gradio** chat UI (needs `OPENAI_API_KEY` and `MCP_SERVER_URL`). `--print-config` prints settings only. Any other arguments → one **CLI** agent turn. On **Hugging Face Spaces**, set secrets for `OPENAI_API_KEY`, `MCP_SERVER_URL`, and `MODEL_NAME`; the Space should run `python app.py` so `PORT` is honored.

`discover_tools.py` and `smoke_product_tools.py` only need `MCP_SERVER_URL`.

Optional live product tests:

```bash
MERIDIAN_PRODUCT_INTEGRATION=1 uv run pytest tests/test_product_integration.py -v
MERIDIAN_ORDER_INTEGRATION=1 uv run pytest tests/test_order_history_integration.py -v
MERIDIAN_CREATE_ORDER_INTEGRATION=1 uv run pytest tests/test_order_placement_integration.py -v
```

`smoke_order_placement.py` and create-order tests **write** orders; use only on the assessment MCP endpoint.

## Hugging Face Space (Stage 15) — your account **tjesctacy**

Profile: **[Oluwatosin Jegede / tjesctacy](https://huggingface.co/tjesctacy)**.

1. **[Create a new Space](https://huggingface.co/new-space)** under **tjesctacy**, choose a name (e.g. `meridian-mcp-chatbot`), SDK **Gradio**, and **connect this GitHub repo** (`Oluwatosin-AiOps/mcp`, branch `main`).  
2. In the Space **Settings → Secrets and variables**, add:
   - **`OPENAI_API_KEY`** (Secret)
   - **`MCP_SERVER_URL`** (same value you use locally — assessment MCP HTTPS URL)
   - **`MODEL_NAME`** = `gpt-4o-mini` (optional; matches local default)  
3. Let the Space **build** (installs from root **`requirements.txt`**). **`PORT`** is set by the platform; `app/ui.py` uses it.  
4. Open **`https://huggingface.co/spaces/tjesctacy/<your-space-name>`**, run one short chat (e.g. list monitors), then take a **screenshot** for the submission rubric.  
5. More detail: [Gradio Spaces](https://huggingface.co/docs/hub/spaces-sdks-gradio), [configuration reference](https://huggingface.co/docs/hub/spaces-config-reference).

## Status

Repo is **Stage 15–ready**: `requirements.txt` exported from `uv.lock`, root **`app.py`** launches Gradio with no args, README includes Space **front matter**. **You** still create the Space under **tjesctacy**, add secrets, verify the live URL, and capture the screenshot. Next: Video 3 / final polish (Stages 16–18 as needed).

Dependency source of truth is **`pyproject.toml`** + **`uv.lock`**. Regenerate **`requirements.txt`** after dependency changes:

```bash
uv export --format requirements-txt --no-hashes --no-annotate > requirements.txt
```
