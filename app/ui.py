"""Gradio chat UI."""

from __future__ import annotations

import os

import gradio as gr

from app.agent import run_agent
from app.config import ConfigurationError, Settings
from app.signin import attempt_sign_in, format_auth_banner

DESCRIPTION = """
Ask about **products**, **stock**, or **search** anytime.

**Flow:** Use **Sign in** (email + PIN) before **orders**, **order history**, or **placing an order**. Stay signed in until **Sign out** or you clear site data for this app. Short replies like **yes** or **proceed** refer to the bot’s last question — keep the chat in one thread.

**Suggested prompts** (type or paste):  
• **Browse:** *List active monitors — list_products with category Monitors and is_active true, then summarize.*  
• **Browse:** *Search for wireless keyboards and mention SKUs and prices from the tool results.*  
• **Orders (after Sign in):** *List my orders with totals and dates.*  
• **Place an order (after Sign in):** First message — *Place the order: 1× COM-0024* (use a real SKU from browse/search). When the bot asks you to confirm, reply — *yes, proceed* — (or spell out quantity/SKU again if you prefer).

**Do not paste API keys or secrets** into this chat.
""".strip()

_EMPTY_AUTH: dict[str, str | None] = {"customer_id": None, "email": None}

_BROWSER_KEY = "meridian_customer_auth_v1"


def _browser_state_secret() -> str | None:
    """Stable secret so localStorage survives server restarts; set in production Docker/env."""
    s = (os.environ.get("MERIDIAN_BROWSER_STATE_SECRET") or "").strip()
    return s or None


async def meridian_chat(
    message: str,
    history: list,
    auth: dict[str, str | None],
) -> tuple[str, dict[str, str | None], str]:
    """Chat turn: reply + updated auth session + account banner markdown."""
    auth = auth if isinstance(auth, dict) else dict(_EMPTY_AUTH)
    cid_raw = auth.get("customer_id")
    cid = cid_raw.strip() if isinstance(cid_raw, str) else None
    email_raw = auth.get("email")
    email = email_raw.strip() if isinstance(email_raw, str) else None

    try:
        settings = Settings.from_env()
    except ConfigurationError as exc:
        banner = format_auth_banner(auth)
        return f"Configuration error: {exc}", auth, banner

    text = (message or "").strip()
    if not text:
        return "Please enter a question.", auth, format_auth_banner(auth)

    reply, new_cid = await run_agent(
        text,
        settings,
        session_verified_customer_id=cid,
        chat_history=history,
    )

    new_auth = {
        "customer_id": new_cid,
        "email": email,
    }
    return reply, new_auth, format_auth_banner(new_auth)


async def on_sign_in(
    email: str,
    pin: str,
    auth: dict[str, str | None],
) -> tuple[dict[str, str | None], str, str, str]:
    """Validate PIN via MCP; update session and clear PIN field on success."""
    _ = auth
    try:
        settings = Settings.from_env()
    except ConfigurationError as exc:
        raise gr.Error(f"Configuration error: {exc}") from exc

    cid, msg = await attempt_sign_in(settings, email, pin)
    if not cid:
        raise gr.Error(msg)

    new_auth = {"customer_id": cid, "email": email.strip()}
    em = email.strip()
    return new_auth, format_auth_banner(new_auth), em, ""


def on_sign_out() -> tuple[dict[str, str | None], str, str, str]:
    """Clear verified session and form fields."""
    empty = dict(_EMPTY_AUTH)
    return empty, format_auth_banner(empty), "", ""


def build_demo() -> gr.Blocks:
    """Chat plus Sign in / Sign out; auth persisted in browser (BrowserState).

    We avoid ``ChatInterface(examples=[...])`` when examples bundled ``auth_session`` inputs:
    Gradio's example runner injects those values and was resetting sign-in to empty on every
    example click. Use the suggested prompts in the description instead.
    """
    with gr.Blocks() as demo:
        auth_session = gr.BrowserState(
            dict(_EMPTY_AUTH),
            storage_key=_BROWSER_KEY,
            secret=_browser_state_secret(),
        )

        gr.Markdown("# Meridian Electronics — Customer Support")

        with gr.Row():
            signin_email = gr.Textbox(
                label="Email",
                placeholder="you@example.com",
                scale=2,
                autofocus=False,
            )
            signin_pin = gr.Textbox(
                label="PIN",
                type="password",
                placeholder="4-digit PIN",
                max_length=16,
                scale=1,
            )
            sign_in_btn = gr.Button("Sign in", variant="primary", scale=1)
            sign_out_btn = gr.Button("Sign out", variant="secondary", scale=1)

        auth_banner = gr.Markdown(value=format_auth_banner(None))

        gr.ChatInterface(
            fn=meridian_chat,
            additional_inputs=[auth_session],
            additional_outputs=[auth_session, auth_banner],
            description=DESCRIPTION,
            examples=None,
            cache_examples=False,
            flagging_mode="never",
            fill_width=True,
        )

        sign_in_btn.click(
            on_sign_in,
            inputs=[signin_email, signin_pin, auth_session],
            outputs=[auth_session, auth_banner, signin_email, signin_pin],
        )
        sign_out_btn.click(
            on_sign_out,
            inputs=None,
            outputs=[auth_session, auth_banner, signin_email, signin_pin],
        )

    return demo


def _server_port() -> int:
    """Parse PORT; empty string falls back to 7860."""
    raw = (os.environ.get("PORT") or os.environ.get("GRADIO_SERVER_PORT") or "7860").strip()
    if not raw:
        return 7860
    return int(raw)


def launch_ui() -> None:
    """Bind all interfaces; port from PORT / GRADIO_SERVER_PORT / 7860."""
    demo = build_demo()
    host = (os.environ.get("GRADIO_SERVER_NAME") or "0.0.0.0").strip() or "0.0.0.0"
    demo.launch(server_name=host, server_port=_server_port())
