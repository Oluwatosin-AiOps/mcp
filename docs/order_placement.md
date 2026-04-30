# Order placement (Stage 10)

## MCP support

The Meridian MCP server exposes **`create_order`** (`customer_id`, `items[]` with `sku`, `quantity`, `unit_price` as string, `currency`).

## Recommended flow (agent + scripts)

1. **`verify_customer_pin`** — unlocks `create_order` only for the verified `customer_id` (see `app/auth_session.py`).
2. **`get_product`** for the SKU — confirms the item exists and supplies an authoritative **price** string for `unit_price`.
3. Confirm **quantity** with the customer (conversation).
4. **`create_order`** — use the verified `customer_id` and line items that match tool-grounded SKUs and prices.

If `create_order` returns an error (unknown SKU, insufficient stock), surface the MCP message—do not invent confirmations.

## Smoke script (creates a real submitted order on the server)

Requires `MCP_SERVER_URL` only. Uses assessment defaults unless you pass arguments:

```bash
uv run python scripts/smoke_order_placement.py
uv run python scripts/smoke_order_placement.py donaldgarcia@example.net 7912 MON-0054 1
```

## Risky integration tests (off by default)

Placing orders mutates backend state. Tests run only when:

```bash
MERIDIAN_CREATE_ORDER_INTEGRATION=1 uv run pytest tests/test_order_placement_integration.py -v
```
