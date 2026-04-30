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

This repository is a **small, explainable** customer-support prototype for **Meridian Electronics**. A user chats in **Gradio** (locally or on **Hugging Face Spaces**); **GPT-4o-mini** decides when to call tools on a remote **MCP server** (Streamable HTTP) so answers about **products**, **stock**, **PIN verification**, **orders**, and **order placement** stay **grounded** in server data instead of invented catalog text.

The **YAML block above** is for [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces-config-reference). GitHub shows the same file; that is normal for a single repo used for both.

---

## Architecture

High-level view (Gradio → agent → MCP → Meridian services):

![Meridian customer support chatbot architecture](docs/arch-diagram.png)

**How this maps to the code (today):**

| Diagram area | Implementation |
|----------------|----------------|
| Gradio UI | `app/ui.py` + root `app.py` (no args → `launch_ui()`) |
| Agent & tool loop | `app/agent.py` — `AsyncOpenAI` + MCP `ClientSession`, up to `MAX_TOOL_ROUNDS` tool rounds per user message |
| Guardrails | `app/guardrails.py` — input checks, assistant secret-pattern filter, reply clipping |
| Auth policy | `app/auth_session.py` — blocks sensitive tools until `verify_customer_pin` succeeds; scopes `customer_id` |
| MCP bridge | `app/mcp_client.py` — tool specs for OpenAI, `call_tool`, `format_tool_result` |
| Config | `app/config.py` — `MCP_SERVER_URL`, `OPENAI_API_KEY`, `MODEL_NAME` from the environment |

The diagram’s **observability** panel (Langfuse / LangSmith, full request tracing) is **aspirational** for this assessment build: the running code focuses on **pytest**, smoke scripts, and clear logs in the terminal—not a hosted tracing stack.

---

## Key decisions

- **No LangChain** — direct OpenAI SDK + official **MCP Python SDK** so every hop is easy to justify in review and in Video 3.
- **GPT-4o-mini** — cost-effective default; override with `MODEL_NAME` if needed.
- **uv** + **`pyproject.toml`** / **`uv.lock`** for dev; root **`requirements.txt`** is **`uv export`** for pip and Hugging Face.
- **PIN gating in code**, not only in the prompt — see `docs/prompt_iterations.md` for how the system prompt was tightened to match `SessionAuthState`.
- **Guardrails** for injection / privilege wording, Unicode normalisation, and `sk-…`-shaped strings — see `docs/guardrails.md`.
- **Integration tests opt-in** via `MERIDIAN_*` env vars so default `pytest` stays offline-safe (`docs/test_results.md`).

---

## Setup

1. Install **[uv](https://docs.astral.sh/uv/installation/)**. Python **3.12** is pinned in `.python-version`.
2. **`uv sync`** — creates `.venv` with locked dependencies.
3. **Environment:** copy `.env.example` → `.env` and set at least **`OPENAI_API_KEY`** and **`MCP_SERVER_URL`**. Never commit `.env`.
4. **Without uv:** Python **3.10+** and **`pip install -r requirements.txt`**.

---

## Run locally

```bash
uv run python app.py                    # Gradio UI (default host/port; uses PORT on Spaces)
uv run python app.py --print-config     # Print MCP URL + model, exit
uv run python app.py "Your question"    # One-shot CLI agent turn
```

**Smoke scripts (MCP only, no LLM):** `scripts/discover_tools.py`, `scripts/smoke_product_tools.py`, `scripts/smoke_order_history.py`, `scripts/smoke_order_placement.py` (placement **writes** orders — assessment endpoint only).

---

## Tests

```bash
uv run pytest
uv run pytest -m "not integration" -q    # fast suite; integration tests deselected
```

Optional live MCP tests: set **`MERIDIAN_PRODUCT_INTEGRATION`**, **`MERIDIAN_ORDER_INTEGRATION`**, or **`MERIDIAN_CREATE_ORDER_INTEGRATION`** to `1` (see `docs/test_results.md`).

---

## Hugging Face Space (account **tjesctacy**)

Profile: **[tjesctacy](https://huggingface.co/tjesctacy)**.

1. **[Create a new Space](https://huggingface.co/new-space)** — owner **tjesctacy**, SDK **Gradio**, link repo **`Oluwatosin-AiOps/mcp`** (branch `main`).
2. **Secrets:** **`OPENAI_API_KEY`**, **`MCP_SERVER_URL`**, optional **`MODEL_NAME`**.
3. Build uses root **`requirements.txt`**; **`PORT`** is set by the platform (handled in `app/ui.py`).
4. Live URL: **`https://huggingface.co/spaces/tjesctacy/<space-name>`** — smoke-test the chat and keep a **screenshot** for submission.

More: [Gradio on Spaces](https://huggingface.co/docs/hub/spaces-sdks-gradio), [Spaces README config](https://huggingface.co/docs/hub/spaces-config-reference).

### Space stuck on “Loading” or “Building”

1. **First build is slow** — installing `requirements.txt` (Gradio, MCP SDK, httpx, etc.) on **CPU Basic** often takes **about 10–20 minutes**. Wait before assuming it is broken.
2. Open **Logs** (or the log panel on the Space page). Check **Build** logs: wait until `pip install` finishes and the container **starts** without error.
3. Open **Runtime / Container** logs. If you see a Python **traceback** (e.g. `ValueError` on `PORT`, import error), fix and `git push hf main` again.
4. Under **Settings → Variables and secrets**, add **`OPENAI_API_KEY`** and **`MCP_SERVER_URL`** as **Secrets**. The UI can still appear without them; the first chat will show a configuration error until they are set.
5. If the build succeeded once but the app is wedged, use **Settings → Factory rebuild**, then wait again for dependency install.

### AWS instead of Spaces?

**S3 alone cannot run this app** (it is not a web server for Python). For a **public URL** on AWS you need **compute** (e.g. **EC2** or **App Runner**) and optionally **HTTPS** in front. See **`docs/aws_deployment.md`** and the repo **`Dockerfile`** for a container you can run on EC2 or push to **ECR** for App Runner.

---

## Documentation

| Doc | Purpose |
|-----|---------|
| `docs/arch-diagram.png` | Architecture figure (same graphic as project root `arch-diagram.png` if present) |
| `docs/problem_framing.md` | Business problem and scope |
| `docs/mcp_tools.md` | Discovered MCP tools summary |
| `docs/guardrails.md` | Guardrail behaviour and limits |
| `docs/test_results.md` | Pytest layout and last captured summary |
| `docs/prompt_iterations.md` | System prompt versions (Stage 16) |
| `docs/project_structure.md` | Directory layout and import boundaries |
| `docs/aws_deployment.md` | AWS options (S3 vs compute), Docker run sketch |

---

## Limitations & improvements

**Limitations**

- **No multi-turn server-side session store** — auth state is **per `run_agent` call**; the UI relies on the model carrying context in the chat thread for a natural conversation.
- **Substring guardrails** — not a complete jailbreak taxonomy; depth is intentionally bounded for the 3-hour-style assessment.
- **No production observability** wired in code (metrics, hosted traces) despite the diagram’s optional tracing box.

**Reasonable next steps**

- Persist minimal session metadata if product requirements grow.
- Expand integration coverage and a tiny **eval** set for regression on tool-choice behaviour.
- Harden rate limiting and redact logs if exposed beyond localhost.

---

## Project layout (quick reference)

| Path | Role |
|------|------|
| `app/config.py` | Environment loading and validation |
| `app/mcp_client.py` | OpenAI tool specs, MCP `tools/call`, result formatting |
| `app/agent.py` | Tool-calling loop over Streamable HTTP MCP |
| `app/guardrails.py` | Input / output safety and clipping |
| `app/auth_session.py` | PIN verification gates sensitive tools |
| `app/ui.py` | Gradio `ChatInterface` |
| `app.py` | Entrypoint: UI, `--print-config`, or CLI |
| `tests/` | pytest |
| `scripts/` | Discovery and smoke scripts |

---

## Status

**Stages 16–17:** `docs/prompt_iterations.md` is populated with three real prompt versions; this README carries **overview, architecture (with diagram), decisions, setup, tests, limitations, and improvements**. **Stage 15** Space deploy and screenshot remain on you at Hugging Face.

Regenerate **`requirements.txt`** after dependency changes:

```bash
uv export --format requirements-txt --no-hashes --no-annotate > requirements.txt
```
