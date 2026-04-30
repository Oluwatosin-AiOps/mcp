"""Lightweight import/build checks for the Gradio UI."""

from __future__ import annotations

import gradio as gr

from app.ui import build_chat_interface


def test_build_chat_interface_returns_chat_interface() -> None:
    demo = build_chat_interface()
    assert isinstance(demo, gr.ChatInterface)
