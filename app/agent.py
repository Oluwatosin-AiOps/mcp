"""OpenAI tool-calling loop against the Meridian MCP server."""

from __future__ import annotations

import json
import sys
from typing import Any

import anyio
from openai import APIStatusError, AsyncOpenAI

from app.auth_session import SessionAuthState
from app.config import ConfigurationError, Settings
from app.guardrails import check_user_message, clip_assistant_reply
from app.mcp_client import call_tool_text, tools_for_openai
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

MAX_TOOL_ROUNDS = 10

SYSTEM_PROMPT = """You are Meridian Electronics customer support.

Rules:
- Use the provided tools for anything about products, stock, customers, PIN verification, or orders. Do not invent SKUs, prices, inventory, or order data.
- Before listing orders, viewing order details, creating orders, or loading a customer profile by id, the user must successfully call verify_customer_pin in this session. The runtime blocks those tools until then.
- After verification, use the customer id from that tool output for list_orders and create_order when needed.
- For product browse/search, use list_products, search_products, or get_product as appropriate.
- Products: only describe rows returned by those tools. If a tool returns no matches, an error, or empty inventory, say so plainly—never invent SKUs, prices, or stock counts.
- If a tool errors, explain briefly in plain language and suggest what the customer can try next.
- If you need an email, PIN, SKU, or quantity, ask clearly.
- Stay concise and professional."""

async def run_agent(user_message: str, settings: Settings) -> str:
    """Single user turn: guardrails → MCP-backed OpenAI tool loop → final reply."""
    gr = check_user_message(user_message)
    if not gr.ok:
        return gr.message

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message.strip()},
    ]

    try:
        async with streamable_http_client(settings.mcp_server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                openai_tools = await tools_for_openai(session)
                auth = SessionAuthState()

                for _ in range(MAX_TOOL_ROUNDS):
                    try:
                        response = await client.chat.completions.create(
                            model=settings.model_name,
                            messages=messages,
                            tools=openai_tools,
                            tool_choice="auto",
                        )
                    except APIStatusError as exc:
                        return clip_assistant_reply(
                            f"The model request failed ({exc.status_code}). Try again shortly."
                        )

                    choice = response.choices[0]
                    msg = choice.message

                    if msg.tool_calls:
                        messages.append(
                            {
                                "role": "assistant",
                                "content": msg.content or "",
                                "tool_calls": [
                                    {
                                        "id": tc.id,
                                        "type": "function",
                                        "function": {
                                            "name": tc.function.name,
                                            "arguments": tc.function.arguments or "{}",
                                        },
                                    }
                                    for tc in msg.tool_calls
                                ],
                            }
                        )
                        for tc in msg.tool_calls:
                            name = tc.function.name
                            try:
                                args = json.loads(tc.function.arguments or "{}")
                                if not isinstance(args, dict):
                                    args = {}
                            except json.JSONDecodeError:
                                args = {}
                            allowed, auth_msg, adj_args = auth.prepare_tool_call(name, args)
                            if allowed:
                                body = await call_tool_text(session, name, adj_args)
                            else:
                                body = auth_msg
                            if name == "verify_customer_pin":
                                auth.record_verify_customer_pin_result(body)
                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tc.id,
                                    "content": body,
                                }
                            )
                        continue

                    text = (msg.content or "").strip()
                    if not text:
                        text = "I could not produce an answer. Try rephrasing your question."
                    return clip_assistant_reply(text)

                return clip_assistant_reply(
                    "Too many tool steps for one request. Please narrow what you need."
                )
    except Exception as exc:
        return clip_assistant_reply(f"Could not reach Meridian systems: {exc}")


def run_cli() -> None:
    """Parse argv and print one agent turn (for local smoke tests)."""
    try:
        settings = Settings.from_env()
    except ConfigurationError as exc:
        raise SystemExit(f"Configuration error: {exc}") from exc

    query = " ".join(sys.argv[1:]).strip() or (
        "Use list_products with category Monitors and summarize what you see."
    )

    async def _run() -> None:
        print(await run_agent(query, settings))

    anyio.run(_run, backend="asyncio")
