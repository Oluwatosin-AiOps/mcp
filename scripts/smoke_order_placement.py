#!/usr/bin/env python3
"""Verify PIN, validate SKU via get_product, place a minimal create_order (MCP only)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import anyio

from app.config import ConfigurationError, Settings
from app.mcp_client import format_tool_result
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

_UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


def _extract_price_usd(product_text: str) -> str | None:
    m = re.search(r"Price:\s*\$([\d.]+)", product_text)
    return m.group(1) if m else None


async def _run(email: str, pin: str, sku: str, quantity: int) -> None:
    settings = Settings.from_env(require_openai_key=False, load_env_file=True)
    url = settings.mcp_server_url

    async with streamable_http_client(url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            print("=== verify_customer_pin ===")
            verify = await session.call_tool(
                "verify_customer_pin", {"email": email, "pin": pin}
            )
            vtext = format_tool_result(verify)
            print(vtext)
            if verify.isError:
                print("\n(Verify failed; not placing order.)")
                return

            match = _UUID_RE.search(vtext)
            if not match:
                print("\n(No customer UUID; stopping.)")
                return
            customer_id = match.group(0)

            print("\n=== get_product ===")
            gp = await session.call_tool("get_product", {"sku": sku})
            gtext = format_tool_result(gp)
            print(gtext)
            if gp.isError:
                print("\n(get_product failed; not placing order.)")
                return

            unit_price = _extract_price_usd(gtext)
            if not unit_price:
                print("\n(Could not parse Price: $x.xx from product text; stopping.)")
                return

            print("\n=== create_order ===")
            payload = {
                "customer_id": customer_id,
                "items": [
                    {
                        "sku": sku,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "currency": "USD",
                    }
                ],
            }
            co = await session.call_tool("create_order", payload)
            print(format_tool_result(co))
            if co.isError:
                print("\n(Order tool reported an error—expected for bad stock/SKU.)")


def main() -> None:
    try:
        email = sys.argv[1] if len(sys.argv) > 1 else "donaldgarcia@example.net"
        pin = sys.argv[2] if len(sys.argv) > 2 else "7912"
        sku = sys.argv[3] if len(sys.argv) > 3 else "MON-0054"
        qty = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        anyio.run(_run, email, pin, sku, qty, backend="asyncio")
    except ConfigurationError as exc:
        raise SystemExit(f"Configuration error: {exc}") from exc
    except ValueError:
        raise SystemExit("quantity must be an integer") from None


if __name__ == "__main__":
    main()
