# Guardrails

Purpose: keep the Meridian support bot **safe to demo** under assessment review—bounded inputs, refusal of common jailbreak and privilege-escalation wording, and a last-line defense if model output echoes secret-shaped strings.

## User input (`check_user_message`)

- Empty / whitespace-only messages are rejected.
- Messages longer than `MAX_USER_MESSAGE_CHARS` are rejected.
- Substrings matching an OpenAI-style secret pattern (e.g. `sk-…`) are rejected so users do not paste keys into chat.
- Prompt-injection and jailbreak phrases (e.g. “ignore previous instructions”, “developer mode”) yield a fixed refusal.
- Privilege-style asks (e.g. “skip verification”, “another customer’s orders”, SQLi clichés) yield a separate refusal clarifying **verified account only**.

Checks use **NFKC Unicode normalization** before substring matching so trivial homoglyph swaps do not bypass filters.

## Model output (`check_assistant_reply`)

- If the assistant text matches the same secret-shaped pattern, it is replaced with a neutral refusal before display (reduces accidental key echo).

Reply length is still capped by `clip_assistant_reply`.

## Limits (explicit)

- Substring lists are **not** complete jailbreak coverage; they document intent and support pytest.
- **Privileged data** and **hallucination** are primarily enforced by **tools-only policy** in the system prompt and MCP-backed facts—not by output semantic classifiers.
