#!/usr/bin/env python3
"""Exercise MCP product tools: monitors, keyboards, printers; unknown SKU."""

from __future__ import annotations

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


async def _run() -> None:
    settings = Settings.from_env(require_openai_key=False, load_env_file=True)
    url = settings.mcp_server_url

    async with streamable_http_client(url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            print("=== list_products: Monitors (active) ===")
            r1 = await session.call_tool(
                "list_products",
                {"category": "Monitors", "is_active": True},
            )
            print(format_tool_result(r1))

            print("\n=== search_products: keyboard ===")
            r2 = await session.call_tool("search_products", {"query": "keyboard"})
            print(format_tool_result(r2))

            print("\n=== search_products: printer ===")
            r3 = await session.call_tool("search_products", {"query": "printer"})
            print(format_tool_result(r3))

            print("\n=== get_product: unknown SKU ===")
            r4 = await session.call_tool("get_product", {"sku": "COM-NONEXISTENT-99999"})
            print(format_tool_result(r4))
            print(f"(structured isError={r4.isError})")


def main() -> None:
    try:
        anyio.run(_run, backend="asyncio")
    except ConfigurationError as exc:
        raise SystemExit(f"Configuration error: {exc}") from exc


if __name__ == "__main__":
    main()
