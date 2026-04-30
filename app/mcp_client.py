"""MCP session helpers: OpenAI-shaped tool specs and tool execution."""

from __future__ import annotations

import json
from typing import Any

import mcp.types as types
from mcp.client.session import ClientSession


def tool_to_openai_function(tool: types.Tool) -> dict[str, Any]:
    """Map an MCP tool definition to OpenAI Chat Completions ``tools[]`` entry."""
    desc = (tool.description or "").strip()
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": desc or f"MCP tool `{tool.name}`.",
            "parameters": tool.inputSchema,
        },
    }


async def tools_for_openai(session: ClientSession) -> list[dict[str, Any]]:
    """List all server tools (paginated) and convert for OpenAI."""
    collected: list[types.Tool] = []
    cursor: str | None = None
    while True:
        if cursor is None:
            page = await session.list_tools()
        else:
            page = await session.list_tools(params=types.PaginatedRequestParams(cursor=cursor))
        collected.extend(page.tools)
        cursor = page.nextCursor
        if not cursor:
            break
    return [tool_to_openai_function(t) for t in collected]


def format_tool_result(result: types.CallToolResult) -> str:
    """Flatten MCP ``CallToolResult`` into a single string for the LLM."""
    parts: list[str] = []
    if result.isError:
        parts.append("Error from tool.")
    for block in result.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
        else:
            parts.append(str(block.model_dump()))
    if result.structuredContent:
        parts.append(json.dumps(result.structuredContent, indent=2))
    out = "\n".join(p for p in parts if p).strip()
    return out if out else "(empty tool result)"


async def call_tool_text(
    session: ClientSession,
    name: str,
    arguments: dict[str, Any] | None,
) -> str:
    """Invoke ``tools/call`` and return text for the model."""
    try:
        raw = await session.call_tool(name, arguments)
    except Exception as exc:
        return f"Tool invocation failed: {exc}"
    return format_tool_result(raw)
