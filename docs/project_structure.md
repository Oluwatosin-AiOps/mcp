# Project structure (Stage 3)

Minimal layout for the Meridian MCP chatbot. Anything not listed here is optional glue (for example `scripts/` for Stage 5 discovery).

```text
app/
  __init__.py       — application package
  config.py         — environment loading and validation
  mcp_client.py     — MCP transport and tool execution via official SDK
  agent.py          — GPT-4o-mini tool-calling loop
  guardrails.py     — input checks, auth rules, refusal paths
  ui.py             — Gradio chat surface
tests/              — pytest
docs/               — framing, MCP notes, test output, prompt log
scripts/            — standalone discovery script (Stage 5)
app.py              — Hugging Face Spaces / local entrypoint
README.md
requirements.txt
.env.example
```

## Import boundaries

- `app.py` should stay thin: load config, call into `app.ui` when the UI exists.
- `app.agent` orchestrates the model and calls `app.mcp_client` for tools; it consults `app.guardrails` before trusting user text or returning sensitive tool output.

This keeps the demo easy to walk in Video 3 without hiding logic behind frameworks.
