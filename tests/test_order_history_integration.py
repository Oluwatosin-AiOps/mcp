"""Live MCP: PIN verify then list_orders. Skip unless MERIDIAN_ORDER_INTEGRATION=1."""

from __future__ import annotations

import os
import re

import anyio
import pytest

from app.config import Settings
from app.mcp_client import format_tool_result
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

pytestmark = pytest.mark.skipif(
    os.environ.get("MERIDIAN_ORDER_INTEGRATION") != "1",
    reason="Set MERIDIAN_ORDER_INTEGRATION=1 for live MCP order history tests",
)

_UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


def test_verify_donald_then_list_orders():
    async def inner() -> None:
        s = Settings.from_env(require_openai_key=False, load_env_file=True)
        async with streamable_http_client(s.mcp_server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                v = await session.call_tool(
                    "verify_customer_pin",
                    {"email": "donaldgarcia@example.net", "pin": "7912"},
                )
                vtext = format_tool_result(v)
                assert not v.isError
                m = _UUID_RE.search(vtext)
                assert m, vtext
                cid = m.group(0)
                o = await session.call_tool("list_orders", {"customer_id": cid})
                otext = format_tool_result(o)
                assert len(otext) > 30
                assert "order" in otext.lower()

    anyio.run(inner, backend="asyncio")


def test_wrong_pin_no_orders_list_extractable():
    async def inner() -> None:
        s = Settings.from_env(require_openai_key=False, load_env_file=True)
        async with streamable_http_client(s.mcp_server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                v = await session.call_tool(
                    "verify_customer_pin",
                    {"email": "donaldgarcia@example.net", "pin": "0000"},
                )
                vtext = format_tool_result(v)
                lower = vtext.lower()
                assert v.isError or "incorrect" in lower or "not found" in lower or "invalid" in lower
                m = _UUID_RE.search(vtext)
                assert m is None

    anyio.run(inner, backend="asyncio")
