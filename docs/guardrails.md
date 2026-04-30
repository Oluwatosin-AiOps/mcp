# Guardrails

## Input (`check_user_message`)

- Empty / too long messages rejected.
- OpenAI-style secret pattern (`sk-…`) rejected on input.
- Injection / jailbreak substrings → refusal.
- Privilege-style asks (skip verify, other customers’ data, SQLi clichés) → separate refusal.
- NFKC normalization before substring checks.

## Output (`check_assistant_reply`)

Secret-shaped strings in assistant text → neutral refusal before display. Length capped via `clip_assistant_reply`.

## Limits

Substring lists are incomplete by design. Facts come from MCP tools + system prompt policy, not semantic classifiers on output.
