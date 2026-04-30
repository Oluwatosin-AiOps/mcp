# MCP tools (discovery)

From `scripts/discover_tools.py` over Streamable HTTP (~8 tools).

| Flow | Tools |
|------|--------|
| Products | `list_products`, `search_products`, `get_product` |
| Auth | `verify_customer_pin`, `get_customer` |
| Orders | `list_orders`, `get_order`, `create_order` |

PIN verification yields a customer UUID for `list_orders` / `create_order`. `create_order` line items must match MCP pricing/inventory; failures return tool errors.

Discovery follows `nextCursor` until done.
