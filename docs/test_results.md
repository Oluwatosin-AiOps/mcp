# Pytest results (Stage 12)

Captured from a full suite run on **2026-04-30**. CI or future runs may differ slightly by Python/pytest versions.

## Default run (offline-safe)

Fast tests only; integration modules **skip** unless `MERIDIAN_*` env vars are set.

```bash
uv run pytest -v
```

```
======================== 36 passed, 8 skipped in 0.52s =========================
```

## What the suite covers

| Area | Module(s) | Notes |
|------|-----------|--------|
| Config validation | `test_config.py` | Required env, URL scheme, optional OpenAI key |
| Auth gating | `test_auth_session.py` | Verify success/failure, `list_orders` / `create_order` / `get_customer` customer id enforcement and **missing-id injection** |
| Guardrails | `test_guardrails.py` | Injection, privilege, NFKC, secret-shaped strings, clipping |
| MCP formatting | `test_mcp_client_format.py` | Tool-to-OpenAI shape, duplicate structured content dedupe |
| Agent boundary | `test_run_agent_guardrails.py` | `run_agent` returns refusal **before** MCP on blocked input |
| Live MCP | `test_product_integration.py`, `test_order_history_integration.py`, `test_order_placement_integration.py` | Marked `@pytest.mark.integration`; opt-in via env (see README) |

## Integration-only run examples

```bash
MERIDIAN_PRODUCT_INTEGRATION=1 uv run pytest tests/test_product_integration.py -v
MERIDIAN_ORDER_INTEGRATION=1 uv run pytest tests/test_order_history_integration.py -v
MERIDIAN_CREATE_ORDER_INTEGRATION=1 uv run pytest tests/test_order_placement_integration.py -v
```

Filter by marker:

```bash
uv run pytest -m "not integration" -q    # 36 passed, 8 deselected (integration tests not collected)
uv run pytest -m integration -v          # integration tests only (still skip inside module without MERIDIAN_* )
```

## Screenshot

If the assessment asks for a screenshot, capture your terminal after `uv run pytest -v` showing **36 passed, 8 skipped** (or the current counts).
