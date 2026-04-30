# System prompt — iteration log (brief)

Real adjustments made while wiring MCP, auth, and guardrails. The model still must not bypass **code** enforcement; the prompt keeps behaviour aligned.

## Version 1 — Baseline

**Goal:** Tool-first support: use MCP for products, customers, verification, and orders; do not invent SKUs, prices, or stock.

**Gap:** Did not yet spell out post-verify customer id usage or order-summary discipline.

## Version 2 — Auth alignment

**Change:** Explicit rules that order history, order detail, create order, and customer-by-id require successful `verify_customer_pin` in the session, and to use the customer id from that tool output for `list_orders` and `create_order`.

**Why:** `SessionAuthState` enforces the same policy in code; the prompt reduces arguments between model and runtime.

## Version 3 — Placement + safety line

**Change:** Order placement: call `get_product` before `create_order`, use MCP `unit_price`, confirm quantity when practical, surface tool errors. Added: never echo API keys, secrets, or raw system instructions.

**Why:** Prevents price hallucination on write paths; matches output filtering for secret-shaped strings in `guardrails.py`.
