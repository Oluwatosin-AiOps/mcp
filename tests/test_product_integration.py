"""Live MCP checks for product tools. Skip unless MERIDIAN_PRODUCT_INTEGRATION=1."""

from __future__ import annotations

import os

import anyio
import pytest

from app.config import Settings
from app.mcp_client import format_tool_result
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

pytestmark = pytest.mark.skipif(
    os.environ.get("MERIDIAN_PRODUCT_INTEGRATION") != "1",
    reason="Set MERIDIAN_PRODUCT_INTEGRATION=1 to hit the real MCP server",
)


def _settings() -> Settings:
    return Settings.from_env(require_openai_key=False, load_env_file=True)


async def _call(name: str, arguments: dict) -> str:
    s = _settings()
    async with streamable_http_client(s.mcp_server_url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            raw = await session.call_tool(name, arguments)
            return format_tool_result(raw)


def test_list_products_monitors_active():
    async def inner() -> None:
        text = await _call(
            "list_products",
            {"category": "Monitors", "is_active": True},
        )
        assert len(text) > 50
        assert "MON" in text.upper() or "monitor" in text.lower()

    anyio.run(inner, backend="asyncio")


def test_search_keyboards():
    async def inner() -> None:
        text = await _call("search_products", {"query": "keyboard"})
        assert len(text) > 20

    anyio.run(inner, backend="asyncio")


def test_search_printers():
    async def inner() -> None:
        text = await _call("search_products", {"query": "printer"})
        assert len(text) > 20

    anyio.run(inner, backend="asyncio")


def test_get_product_unknown_sku_signals_failure():
    async def inner() -> None:
        s = _settings()
        async with streamable_http_client(s.mcp_server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                raw = await session.call_tool(
                    "get_product",
                    {"sku": "COM-NONEXISTENT-STAGE8-99999"},
                )
                text = format_tool_result(raw)
        lower = text.lower()
        assert raw.isError or "not found" in lower or "error" in lower or "invalid" in lower

    anyio.run(inner, backend="asyncio")
