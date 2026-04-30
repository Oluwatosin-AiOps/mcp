#!/usr/bin/env python3
"""Verify PIN then list_orders via MCP (no LLM)."""

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


async def _run(email: str, pin: str) -> None:
    settings = Settings.from_env(require_openai_key=False, load_env_file=True)
    url = settings.mcp_server_url

    async with streamable_http_client(url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            print("=== verify_customer_pin ===")
            verify = await session.call_tool(
                "verify_customer_pin",
                {"email": email, "pin": pin},
            )
            vtext = format_tool_result(verify)
            print(vtext)

            match = _UUID_RE.search(vtext)
            if not match:
                print("\n(No customer UUID found in verify output; stopping.)")
                return

            customer_id = match.group(0)
            print(f"\n(using customer_id {customer_id})\n")

            print("=== list_orders ===")
            orders = await session.call_tool(
                "list_orders",
                {"customer_id": customer_id},
            )
            print(format_tool_result(orders))


def main() -> None:
    try:
        email = sys.argv[1] if len(sys.argv) > 1 else "donaldgarcia@example.net"
        pin = sys.argv[2] if len(sys.argv) > 2 else "7912"
        anyio.run(_run, email, pin, backend="asyncio")
    except ConfigurationError as exc:
        raise SystemExit(f"Configuration error: {exc}") from exc


if __name__ == "__main__":
    main()
