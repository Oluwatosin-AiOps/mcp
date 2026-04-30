"""Gradio chat UI — Meridian MCP support bot (Stage 13)."""

from __future__ import annotations

import os

import gradio as gr

from app.agent import run_agent
from app.config import ConfigurationError, Settings

DESCRIPTION = """
Ask about **products**, **stock**, **search**, or **orders**. Sensitive actions (order history, placing orders, customer profile by id) require **PIN verification** in the same conversation first.

**Do not paste API keys or secrets** into this chat.
""".strip()

EXAMPLES = [
    "List active monitors: use list_products with category Monitors and is_active true, then summarize.",
    "Search for wireless keyboards and mention SKUs and prices from the tool results.",
    "Verify donaldgarcia@example.net with PIN 7912, then list my orders with totals and dates.",
]


async def meridian_chat(message: str, history: list) -> str:
    """Gradio ChatInterface callback; returns assistant text only."""
    try:
        settings = Settings.from_env()
    except ConfigurationError as exc:
        return f"Configuration error: {exc}"
    text = (message or "").strip()
    if not text:
        return "Please enter a question."
    return await run_agent(text, settings)


def build_chat_interface() -> gr.ChatInterface:
    return gr.ChatInterface(
        fn=meridian_chat,
        title="Meridian Electronics — Customer Support",
        description=DESCRIPTION,
        examples=EXAMPLES,
        cache_examples=False,
        flagging_mode="never",
        fill_width=True,
    )


def launch_ui() -> None:
    """Listen on all interfaces; respect PORT for Hugging Face Spaces."""
    demo = build_chat_interface()
    port = int(os.environ.get("PORT", os.environ.get("GRADIO_SERVER_PORT", "7860")))
    demo.launch(server_name="0.0.0.0", server_port=port)
