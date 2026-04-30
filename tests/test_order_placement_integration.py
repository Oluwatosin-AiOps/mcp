"""Live create_order checks; mutates server state — MERIDIAN_CREATE_ORDER_INTEGRATION=1 only."""

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
    os.environ.get("MERIDIAN_CREATE_ORDER_INTEGRATION") != "1",
    reason="Set MERIDIAN_CREATE_ORDER_INTEGRATION=1 (creates real orders)",
)

_UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


def _price_from_product(text: str) -> str | None:
    m = re.search(r"Price:\s*\$([\d.]+)", text)
    return m.group(1) if m else None


def test_create_order_happy_path_small_quantity():
    async def inner() -> None:
        s = Settings.from_env(require_openai_key=False, load_env_file=True)
        sku = "MON-0054"
        async with streamable_http_client(s.mcp_server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                v = await session.call_tool(
                    "verify_customer_pin",
                    {"email": "donaldgarcia@example.net", "pin": "7912"},
                )
                assert not v.isError
                vtext = format_tool_result(v)
                m = _UUID_RE.search(vtext)
                assert m
                cid = m.group(0)

                gp = await session.call_tool("get_product", {"sku": sku})
                assert not gp.isError
                gtext = format_tool_result(gp)
                price = _price_from_product(gtext)
                assert price

                co = await session.call_tool(
                    "create_order",
                    {
                        "customer_id": cid,
                        "items": [
                            {
                                "sku": sku,
                                "quantity": 1,
                                "unit_price": price,
                                "currency": "USD",
                            }
                        ],
                    },
                )
                ctext = format_tool_result(co)
                assert not co.isError, ctext
                lower = ctext.lower()
                assert "order" in lower or "submitted" in lower or "pending" in lower

    anyio.run(inner, backend="asyncio")


def test_create_order_bad_sku_fails():
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
                cid = _UUID_RE.search(vtext)
                assert cid
                co = await session.call_tool(
                    "create_order",
                    {
                        "customer_id": cid.group(0),
                        "items": [
                            {
                                "sku": "COM-FAKE-SKU-STAGE10",
                                "quantity": 1,
                                "unit_price": "9.99",
                                "currency": "USD",
                            }
                        ],
                    },
                )
                assert co.isError or "not found" in format_tool_result(co).lower()

    anyio.run(inner, backend="asyncio")
