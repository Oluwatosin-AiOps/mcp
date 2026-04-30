# Pytest

Offline default: integration tests skip unless `MERIDIAN_*=1`.

```bash
uv run pytest -v
uv run pytest -m "not integration" -q
```

Example outcome (counts drift over time): ~37 passed, 8 skipped without live MCP env.

| Area | Tests |
|------|--------|
| Config | `test_config.py` |
| Auth | `test_auth_session.py` |
| Guardrails | `test_guardrails.py`, `test_run_agent_guardrails.py` |
| MCP format | `test_mcp_client_format.py` |
| UI import | `test_ui_smoke.py` |
| Live MCP | `test_*_integration.py` (`@pytest.mark.integration`) |

```bash
MERIDIAN_PRODUCT_INTEGRATION=1 uv run pytest tests/test_product_integration.py -v
MERIDIAN_ORDER_INTEGRATION=1 uv run pytest tests/test_order_history_integration.py -v
MERIDIAN_CREATE_ORDER_INTEGRATION=1 uv run pytest tests/test_order_placement_integration.py -v
```
