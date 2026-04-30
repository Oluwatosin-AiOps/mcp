# Order history (Stage 9)

## Policy

- **Authentication:** `list_orders` and `get_order` are **gated in the agent** until `verify_customer_pin` succeeds in that turn (`app/auth_session.py`). The model cannot reach those MCP calls earlier without receiving the policy message as the tool result.
- **Scope:** After verification, `list_orders` arguments are forced to the **verified customer id** when omitted, and **rejected** if the model passes a different `customer_id`.

## MCP tools

| Step | Tool | Notes |
|------|------|--------|
| 1 | `verify_customer_pin` | `email`, `pin` — assessment users in `docs/auth_test_users.md` |
| 2 | `list_orders` | Optional `customer_id`, `status`; use verified id |
| 3 | `get_order` | `order_id` — detail view with line items |

## Assistant behaviour

The system prompt asks for **clear summaries**: order id, status, payment state, total, created date. Raw MCP strings are authoritative; the model should not invent orders.

## Smoke script (terminal)

Requires `MCP_SERVER_URL` only:

```bash
uv run python scripts/smoke_order_history.py
uv run python scripts/smoke_order_history.py michellejames@example.com 1520
```

## Optional integration tests

```bash
MERIDIAN_ORDER_INTEGRATION=1 uv run pytest tests/test_order_history_integration.py -v
```
