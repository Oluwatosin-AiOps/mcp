"""User input checks and light output clipping."""

from __future__ import annotations

from dataclasses import dataclass

MAX_USER_MESSAGE_CHARS = 6000
MAX_ASSISTANT_REPLY_CHARS = 12000

_INJECTION_MARKERS = (
    "ignore previous",
    "ignore all previous",
    "system prompt",
    "reveal your instructions",
    "bypass authentication",
    "show all orders",
    "dump your prompt",
)


@dataclass(frozen=True)
class GuardrailResult:
    ok: bool
    message: str


def check_user_message(text: str) -> GuardrailResult:
    stripped = text.strip()
    if not stripped:
        return GuardrailResult(False, "Please enter a question or request.")
    if len(stripped) > MAX_USER_MESSAGE_CHARS:
        return GuardrailResult(False, "That message is too long. Please shorten it.")
    lower = stripped.lower()
    for phrase in _INJECTION_MARKERS:
        if phrase in lower:
            return GuardrailResult(
                False,
                "I cannot follow that instruction. Ask about Meridian products, orders, or account verification.",
            )
    return GuardrailResult(True, "")


def clip_assistant_reply(text: str, max_chars: int = MAX_ASSISTANT_REPLY_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 24].rstrip() + "\n…(truncated)"
