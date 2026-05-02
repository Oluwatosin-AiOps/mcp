"""Explicit UI sign-in via MCP verify_customer_pin (no LLM)."""

from __future__ import annotations

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

from app.auth_session import SessionAuthState
from app.config import Settings
from app.mcp_client import call_tool_text


async def verify_pin_via_mcp(settings: Settings, email: str, pin: str) -> str:
    """Call ``verify_customer_pin`` and return the flattened tool text."""
    email = email.strip()
    pin = pin.strip()
    async with streamable_http_client(settings.mcp_server_url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            return await call_tool_text(
                session,
                "verify_customer_pin",
                {"email": email, "pin": pin},
            )


async def attempt_sign_in(settings: Settings, email: str, pin: str) -> tuple[str | None, str]:
    """
    Try MCP PIN verification. Returns ``(customer_id_or_none, short_message_for_UI)``.
    """
    email = email.strip()
    pin = pin.strip()
    if not email:
        return None, "Enter your email address."
    if not pin:
        return None, "Enter your 4-digit PIN."
    try:
        body = await verify_pin_via_mcp(settings, email, pin)
    except Exception as exc:  # noqa: BLE001 — surface connectivity failures in UI
        return None, f"Could not reach Meridian: {exc}"

    auth = SessionAuthState()
    auth.record_verify_customer_pin_result(body)
    if auth.verified_customer_id:
        return auth.verified_customer_id, "Signed in successfully."
    return None, "Sign in failed. Check your email and PIN, then try again."


def format_auth_banner(auth: dict | None) -> str:
    """Markdown line for the account strip above the chat."""
    auth = auth or {}
    cid = auth.get("customer_id")
    email = auth.get("email")
    if not cid:
        return (
            "**Account:** Not signed in. Use **Sign in** (email + PIN) before "
            "**orders**, **order history**, or **placing an order**. "
            "Product questions work without signing in."
        )
    if email:
        return f"**Account:** Signed in as **{email}**. Click **Sign out** when you are done."
    return "**Account:** Signed in (verified in this chat). Click **Sign out** when you are done."
