"""Lightweight import/build checks for the Gradio UI."""

from __future__ import annotations

import gradio as gr

from app.ui import build_demo


def test_build_demo_returns_blocks() -> None:
    demo = build_demo()
    assert isinstance(demo, gr.Blocks)
