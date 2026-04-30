# MCP server tools (discovery notes)

Source: `scripts/discover_tools.py` against `MCP_SERVER_URL` (Streamable HTTP). Eight tools total.

## Mapping to Meridian flows

| Flow | Tools |
|------|--------|
| Product availability | `list_products` (optional `category`, `is_active`), `get_product` (`sku`), `search_products` (`query`) |
| Authentication | `verify_customer_pin` (`email`, `pin`) returns customer details when valid; `get_customer` (`customer_id`) for lookups when UUID is known |
| Order history | `list_orders` (optional `customer_id`, `status`), `get_order` (`order_id`) |
| Order placement | `create_order` (`customer_id`, `items[]` with `sku`, `quantity`, `unit_price`, `currency`) |

## Agent implications

- After PIN verification, the response should expose a **customer id** (UUID) for `list_orders` / `create_order`. The agent must thread that id rather than guessing.
- `create_order` expects structured line items and validates inventory; failures surface as tool errors (`ProductNotFoundError`, `InsufficientInventoryError`, etc.).
- Product answers must come from these tools only (no invented SKUs or stock).

## Pagination

`tools/list` supports cursors; the discovery script follows `nextCursor` until exhausted.
