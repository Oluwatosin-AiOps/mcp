# Stage 1 — Problem framing

This note matches the Meridian assessment brief and the Video 1 narrative: what we are building, how we will know it works, and what we will not do in the time box.

## Business problem

Meridian Electronics sells computer products (monitors, keyboards, printers, networking, accessories). Support handles customer requests manually by phone and email. Leadership wants a prototype that shows whether an AI assistant can handle common requests **without** sacrificing accuracy, trust, or alignment with real backend behavior.

The assistant is not a standalone chat surface: it is a **controlled interface** to internal systems. Business operations must go through the MCP server (`Streamable HTTP`), which acts as the gateway to existing services rather than direct database access.

## Core flows

The chatbot must support these scenarios via MCP tools (exact tool names come from discovery in Stage 5):

1. **Product availability** — Answer what is available using MCP-backed data, not free-form guesses.
2. **Authentication** — Identify returning customers (email + PIN as provided in the assessment test data).
3. **Order history** — Retrieve history only after successful authentication.
4. **Order placement** — Place orders when the MCP surface supports it; otherwise state the limitation clearly.

## Success criteria (testable)

| # | Criterion | How we verify |
|---|-----------|----------------|
| 1 | MCP tools are discovered and used deliberately | Discovery script output documented; agent calls match tool schemas. |
| 2 | Authentication behaves correctly | Valid email + PIN succeeds; wrong PIN fails; unknown email handled; tests cover cases. |
| 3 | Sensitive data gated | Order history blocked without auth; allowed after auth. |
| 4 | Product answers grounded | Responses driven by MCP product tools; empty or invalid queries handled without inventing inventory. |
| 5 | Abuse and bad inputs handled | Guardrails + tests for injection-style prompts and missing parameters. |
| 6 | At least one full customer path end-to-end | e.g. auth → history, or product lookup → clear outcome, documented in demo and tests. |
| 7 | Deliverable quality | Deployable (Hugging Face Spaces target), covered by pytest where practical, architecture explainable in review. |

## Architecture (summary)

Layers, bottom to top:

- **MCP server** — Business operations (products, auth, orders) exposed as tools.
- **MCP client** — Official Python `mcp` SDK over Streamable HTTP; discovery and tool execution.
- **Agent** — GPT-4o-mini with tool calling; maps user intent to tool use without unnecessary abstraction (no LangChain).
- **Guardrails** — Input validation, auth rules, prompt-injection resistance, safe refusals.
- **UI** — Gradio chat; deployed to Hugging Face Spaces for a live demo URL.

This separation keeps the prototype aligned with how a production system would bound trust and capability.

## Execution order (priorities)

1. Connect to MCP and run **tool discovery**; document findings before heavy agent logic.
2. Implement **core agent** and one **working vertical slice** (likely product lookup or authentication first).
3. Add **edge cases**, **pytest**, and **guardrails** so behavior is defensible under review.
4. Wire **Gradio** and **deploy** to Hugging Face Spaces.

Assessment priority reminder: **MCP → Agent → UI → Tests → Deploy**, adjusted only if discovery blocks the agent.

## Scope cuts (explicit non-goals for the prototype window)

- **Advanced UI** — Polish and secondary UX beyond a clear, functional chat.
- **Deep observability dashboards** — No full tracing UI or metrics stack; minimal logging acceptable.
- **Full workflow coverage** — Depth over breadth: one or two flows finished with tests and safety beats shallow coverage everywhere.

If time runs short, remaining flows are described honestly in README and Video 3 rather than half-implemented.

## Principle

Ship a **minimal but credible** prototype: functionality plus engineering judgment, safety, and a path to production review—not the largest possible feature surface.
