"""Convert Gradio Chatbot history into OpenAI Chat Completions messages."""

from __future__ import annotations

from typing import Any

# Cap turns so we stay within context limits (each entry can be multi-part).
MAX_HISTORY_MESSAGES = 48


def _text_from_gradio_content(content: Any) -> str:
    """Flatten Gradio message content to plain text for the model."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, dict):
        # Normalized part: {"type": "text", "text": "..."}
        if content.get("type") == "text" and "text" in content:
            return str(content["text"]).strip()
        # Legacy simple dict
        if "text" in content and "type" not in content:
            return str(content["text"]).strip()
        return ""
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            t = _text_from_gradio_content(block)
            if t:
                parts.append(t)
        return "\n".join(parts).strip()
    return str(content).strip()


def gradio_history_to_openai_messages(history: Any) -> list[dict[str, Any]]:
    """
    Map Gradio chat history (without the current user message) to OpenAI-style messages.

    Only ``user`` and ``assistant`` roles are kept; empty messages are skipped.
    """
    if not history or not isinstance(history, list):
        return []

    out: list[dict[str, Any]] = []
    for msg in history[-MAX_HISTORY_MESSAGES:]:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role")
        if role not in ("user", "assistant"):
            continue
        text = _text_from_gradio_content(msg.get("content"))
        if not text:
            continue
        out.append({"role": role, "content": text})
    return out
