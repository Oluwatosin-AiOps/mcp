"""User input checks and light output clipping."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

MAX_USER_MESSAGE_CHARS = 6000
MAX_ASSISTANT_REPLY_CHARS = 12000

REFUSAL_INJECTION = (
    "I cannot follow that instruction. Ask about Meridian products, orders, or account verification."
)
REFUSAL_PRIVILEGED = (
    "I can only help with public product information and your own verified Meridian account. "
    "I cannot bypass verification or access other customers' data."
)
REFUSAL_SECRET_INPUT = (
    "Do not share secrets or keys in chat. Ask about products, orders, or verification steps instead."
)
REFUSAL_ASSISTANT_LEAK = (
    "I cannot display that reply. Please rephrase your question about Meridian products or your account."
)

# User-supplied text that looks like an OpenAI-style secret (blocks accidental pastes).
_SECRET_TOKEN_PATTERN = re.compile(
    r"\bsk-(?:proj-|live-|test-)?[a-zA-Z0-9_-]{16,}\b",
    re.IGNORECASE,
)

_INJECTION_MARKERS = (
    "ignore previous",
    "ignore all previous",
    "disregard previous",
    "disregard all previous",
    "forget your instructions",
    "forget everything above",
    "system prompt",
    "reveal your instructions",
    "show your instructions",
    "dump your prompt",
    "what are your instructions",
    "you are now",
    "developer mode",
    "jailbreak",
    "dan mode",
    "without restrictions",
    "bypass authentication",
    "bypass verification",
    "show all orders",
    "list every customer",
    "export all users",
)

_PRIVILEGE_MARKERS = (
    "skip verification",
    "without verifying",
    "fake the verification",
    "pretend i verified",
    "another customer's orders",
    "different customer's",
    "someone else's orders",
    "all orders for every",
    "sql injection",
    "drop table",
)


def _normalize_guard_text(text: str) -> str:
    """NFKC so visually similar glyphs cannot trivially evade substring checks."""
    return unicodedata.normalize("NFKC", text).lower()


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
    if _SECRET_TOKEN_PATTERN.search(stripped):
        return GuardrailResult(False, REFUSAL_SECRET_INPUT)

    lower = _normalize_guard_text(stripped)
    for phrase in _INJECTION_MARKERS:
        if phrase in lower:
            return GuardrailResult(False, REFUSAL_INJECTION)
    for phrase in _PRIVILEGE_MARKERS:
        if phrase in lower:
            return GuardrailResult(False, REFUSAL_PRIVILEGED)
    return GuardrailResult(True, "")


def check_assistant_reply(text: str) -> GuardrailResult:
    """Last-resort filter before returning model text to the user."""
    if _SECRET_TOKEN_PATTERN.search(text):
        return GuardrailResult(False, REFUSAL_ASSISTANT_LEAK)
    return GuardrailResult(True, "")


def clip_assistant_reply(text: str, max_chars: int = MAX_ASSISTANT_REPLY_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 24].rstrip() + "\n…(truncated)"
