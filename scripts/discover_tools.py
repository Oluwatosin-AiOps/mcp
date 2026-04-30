#!/usr/bin/env python3
"""Connect to the Meridian MCP server (Streamable HTTP) and print all tools."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Repo root on path when invoked as scripts/discover_tools.py
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import anyio

from app.config import ConfigurationError, Settings
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.types import PaginatedRequestParams


async def _list_all_tools(url: str) -> None:
    async with streamable_http_client(url) as (read_stream, write_stream, _get_session_id):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            cursor: str | None = None
            n = 0
            while True:
                if cursor is None:
                    page = await session.list_tools()
                else:
                    page = await session.list_tools(params=PaginatedRequestParams(cursor=cursor))

                for tool in page.tools:
                    n += 1
                    print(f"\n--- Tool {n}: {tool.name} ---")
                    if tool.description:
                        print(tool.description.strip())
                    print("inputSchema:")
                    print(json.dumps(tool.inputSchema, indent=2))
                    if tool.outputSchema:
                        print("outputSchema:")
                        print(json.dumps(tool.outputSchema, indent=2))

                cursor = page.nextCursor
                if not cursor:
                    break

            print(f"\n---\nTotal tools listed: {n}")


def main() -> None:
    try:
        settings = Settings.from_env(require_openai_key=False, load_env_file=True)
    except ConfigurationError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    try:
        anyio.run(_list_all_tools, settings.mcp_server_url, backend="asyncio")
    except Exception as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
