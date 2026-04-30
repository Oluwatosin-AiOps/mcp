# Meridian Electronics — MCP Customer Support Chatbot

Prototype chatbot that uses the official MCP Python SDK and OpenAI tool calling to reach Meridian’s order MCP server.

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
| `app/guardrails.py` | User input checks and reply clipping |
| `app/ui.py` | Gradio chat UI |
| `tests/` | pytest |
| `docs/` | Problem framing, MCP discovery notes, test results, prompt log |
| `scripts/` | Standalone tool discovery (Stage 5) |
| `app.py` | Space/local entrypoint |

See `docs/project_structure.md` for the tree and import boundaries.

## Commands

```bash
uv run pytest
uv run python app.py
uv run python app.py "Search for wireless keyboards and summarize."
uv run python scripts/discover_tools.py
```

`app.py` with no extra arguments only prints config. With a message, it runs one agent turn (needs `OPENAI_API_KEY` and `MCP_SERVER_URL`). `discover_tools.py` only needs `MCP_SERVER_URL`.

## Status

Stages 0–6 complete through the MCP-backed agent. Next: tighten auth and flows (Stages 7–8).

Dependency source of truth is **`pyproject.toml`** + **`uv.lock`**. Regenerate **`requirements.txt`** after dependency changes:

```bash
uv export --format requirements-txt --no-hashes --no-annotate > requirements.txt
```
