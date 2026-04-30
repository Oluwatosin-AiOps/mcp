# Project structure (Stage 3)

Minimal layout for the Meridian MCP chatbot. Anything not listed here is optional glue (for example `scripts/` for Stage 5 discovery).

```text
app/
  __init__.py       — application package
  config.py         — environment loading and validation
  mcp_client.py     — tool definitions for OpenAI; call tools; format results
  agent.py          — async MCP session + OpenAI tool loop
  guardrails.py     — input limits, injection/privilege refusal, sk-* pattern filter; reply clipping
  auth_session.py   — verify_customer_pin unlocks sensitive MCP tools
  ui.py             — Gradio chat surface
tests/              — pytest
docs/               — framing, MCP notes, guardrails, **test_results.md**, prompt log
scripts/            — discovery + smoke scripts (`smoke_order_placement.py` mutates orders); see `docs/`
app.py              — Hugging Face Spaces / local entrypoint
pyproject.toml      — declared dependencies (uv)
uv.lock             — locked versions
.python-version     — interpreter pin for uv
README.md
requirements.txt    — exported from uv for pip / Hugging Face Spaces
.env.example
```

## Import boundaries

- `app.py` should stay thin: load config, call into `app.ui` when the UI exists.
- `app.agent` orchestrates the model and calls `app.mcp_client` for tools; it consults `app.guardrails` before trusting user text or returning sensitive tool output.

This keeps the demo easy to walk in Video 3 without hiding logic behind frameworks.
