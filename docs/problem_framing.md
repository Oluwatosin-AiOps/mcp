# Problem framing

## Problem

Meridian Electronics sells PC gear; support is manual. This prototype is a controlled MCP‑backed assistant: real catalog and orders via tools, not invented facts.

## Flows

1. Product availability (MCP product tools).
2. Authentication (email + PIN).
3. Order history after auth.
4. Order placement when MCP allows it.

## Success criteria

| Criterion | Check |
|-----------|--------|
| Tools discovered and used deliberately | Discovery script + agent matches schemas |
| Auth | Valid PIN succeeds; wrong PIN / unknown email fail; tests |
| Gating | No order/account tools before verify |
| Grounded products | Tool output only; empty/error handled |
| Abuse | Guardrails + tests |
| End‑to‑end path | e.g. verify → orders or product lookup |
| Ship quality | Tests, deploy target, README |

## Stack (summary)

MCP server → MCP client (`mcp` SDK) → agent (GPT‑4o-mini tools) → guardrails → Gradio.

## Non‑goals

Heavy UI polish, full observability stack, exhaustive workflow breadth—prefer depth on one path with tests.
