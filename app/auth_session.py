"""Per-turn auth: PIN verification gates sensitive MCP tools."""

from __future__ import annotations

import re
from typing import Any

_UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)

_SENSITIVE_TOOLS = frozenset({"list_orders", "get_order", "create_order", "get_customer"})


def normalize_session_customer_id(value: str | None) -> str | None:
    """Accept only a full UUID string for cross-turn session trust (no user-supplied garbage)."""
    if not value or not isinstance(value, str):
        return None
    s = value.strip()
    return s if _UUID_RE.fullmatch(s) else None


class SessionAuthState:
    """Tracks verified customer id for one agent turn.

    ``prior_verified_customer_id`` comes from Gradio session state so multi-turn chat stays
    authenticated without re-entering PIN every message.
    """

    __slots__ = ("verified_customer_id",)

    def __init__(self, prior_verified_customer_id: str | None = None) -> None:
        self.verified_customer_id: str | None = normalize_session_customer_id(
            prior_verified_customer_id
        )

    def record_verify_customer_pin_result(self, tool_body: str) -> None:
        """Update session from verify tool output.

        On **success**, set ``verified_customer_id`` from the tool text.
        On **failure**, leave the session unchanged so a spurious or mistaken
        ``verify_customer_pin`` call (common after product tools) does not undo
        **Sign in** or a prior successful verify.
        """
        lower = tool_body.lower()
        if _verify_failed_heuristic(lower):
            return
        match = _UUID_RE.search(tool_body)
        if match:
            self.verified_customer_id = match.group(0)

    def prepare_tool_call(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> tuple[bool, str, dict[str, Any]]:
        """
        Returns ``(allowed, error_message, arguments_to_use)``.

        When ``allowed`` is False, ``error_message`` is returned to the model as the tool result.
        """
        args = dict(arguments)

        if tool_name not in _SENSITIVE_TOOLS:
            return True, "", args

        if not self.verified_customer_id:
            return (
                False,
                "Policy: verify email and PIN with verify_customer_pin before orders or account lookups.",
                args,
            )

        # Always bind order/account tools to the verified session id. The model often guesses a
        # wrong UUID from names in chat; mismatches used to block legitimate Sign-in sessions.
        verified = self.verified_customer_id

        if tool_name == "list_orders":
            args["customer_id"] = verified
            return True, "", args

        if tool_name == "create_order":
            args["customer_id"] = verified
            return True, "", args

        if tool_name == "get_customer":
            args["customer_id"] = verified
            return True, "", args

        if tool_name == "get_order":
            return True, "", args

        return True, "", args


def _verify_failed_heuristic(lower: str) -> bool:
    return (
        "not found" in lower
        or "incorrect" in lower
        or "invalid" in lower
        or "customernotfound" in lower
        or "tool invocation failed" in lower
        or "error from tool" in lower
    )
