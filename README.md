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

## Project layout

- `app/` — MCP client, agent, guardrails, UI modules
- `tests/` — pytest
- `docs/` — notes, test results, prompt log (later stages)
- `app.py` — deploy entrypoint (Gradio in Stage 13)

## Commands

```bash
pytest
```

## Status

Stage 0 scaffold complete — MCP discovery and agent logic follow in later stages.
