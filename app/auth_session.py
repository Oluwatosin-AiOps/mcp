"""Per-turn auth: PIN verification gates sensitive MCP tools."""

from __future__ import annotations

import re
from typing import Any

_UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)

_SENSITIVE_TOOLS = frozenset({"list_orders", "get_order", "create_order", "get_customer"})


class SessionAuthState:
    """Tracks verified customer id for one agent turn (reset each ``run_agent`` call)."""

    __slots__ = ("verified_customer_id",)

    def __init__(self) -> None:
        self.verified_customer_id: str | None = None

    def record_verify_customer_pin_result(self, tool_body: str) -> None:
        """If PIN verification succeeded, capture customer UUID from tool text."""
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

        if tool_name == "list_orders":
            cid = args.get("customer_id")
            if cid is None:
                args["customer_id"] = self.verified_customer_id
            elif cid != self.verified_customer_id:
                return (
                    False,
                    "You can only list orders for the customer you verified.",
                    args,
                )
            return True, "", args

        if tool_name == "create_order":
            if args.get("customer_id") != self.verified_customer_id:
                return (
                    False,
                    "Orders can only be created for the verified customer id.",
                    args,
                )
            return True, "", args

        if tool_name == "get_customer":
            if args.get("customer_id") != self.verified_customer_id:
                return (
                    False,
                    "You can only load the customer profile for the verified account.",
                    args,
                )
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
