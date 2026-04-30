# Product availability

Meridian inventory is **only** accessed through MCP tools:

| Tool | Use |
|------|-----|
| `list_products` | Optional `category` (e.g. `Monitors`), `is_active` |
| `search_products` | `query` string — good for “keyboard”, “printer”, partial names |
| `get_product` | Required `sku` — detail lookup |

## Categories vs search

The server examples mention categories like **Computers** and **Monitors**. For **keyboards** and **printers**, `search_products` is reliable even when the exact category label varies.

## Missing SKU / empty results

- `get_product` with an unknown SKU returns an error-style payload from MCP; the agent must surface that without inventing a product.
- If `list_products` / `search_products` return an empty or terse string, the assistant should say **no matches** instead of guessing.

## Smoke script (terminal / video)

Requires `MCP_SERVER_URL` in `.env` (no OpenAI key):

```bash
uv run python scripts/smoke_product_tools.py
```

## Optional pytest against live MCP

```bash
MERIDIAN_PRODUCT_INTEGRATION=1 uv run pytest tests/test_product_integration.py -v
```

Unset the variable (default) to skip these tests in environments without the server.
