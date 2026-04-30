# Meridian Electronics — MCP Customer Support Chatbot

Prototype chatbot that uses the official MCP Python SDK and OpenAI tool calling to reach Meridian’s order MCP server.

## Setup (Stage 0)

1. **Python 3.10+** is required (the `mcp` package does not install on 3.9).

2. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

   If your default `python3` is older than 3.10, use a newer runtime (e.g. install from [python.org](https://www.python.org/downloads/) or use [uv](https://docs.astral.sh/uv/): `uv venv --python 3.12 .venv` then `uv pip install -r requirements.txt --python .venv/bin/python`).

3. **Environment:** copy `.env.example` to `.env` and set `OPENAI_API_KEY`. Never commit `.env`.

4. **GitHub repo:** create an empty repository on GitHub (e.g. under your user or org), then:

   ```bash
   git remote add origin https://github.com/<your-account>/<your-repo>.git
   git branch -M main
   git push -u origin main
   ```

## Project layout (Stage 3)

| Path | Role |
|------|------|
| `app/config.py` | Load `.env`, validate `MCP_SERVER_URL`, `OPENAI_API_KEY`, `MODEL_NAME` |
| `app/mcp_client.py` | MCP session and tool calls (official Python SDK) |
| `app/agent.py` | LLM tool-calling loop |
| `app/guardrails.py` | Validation, auth enforcement, unsafe prompt handling |
| `app/ui.py` | Gradio chat UI |
| `tests/` | pytest |
| `docs/` | Problem framing, MCP discovery notes, test results, prompt log |
| `scripts/` | Standalone tool discovery (Stage 5) |
| `app.py` | Space/local entrypoint |

See `docs/project_structure.md` for the tree and import boundaries.

## Commands

```bash
pytest
```

## Status

Stages 0–3 complete: scaffold, framing, Video 1, and documented layout. Next: config validation (Stage 4) and MCP discovery (Stage 5).
