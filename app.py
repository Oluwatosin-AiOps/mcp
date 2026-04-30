"""
Hugging Face Spaces / local entrypoint for the Gradio UI.

Without arguments: print config. With arguments: run one agent turn (Stage 6 smoke test).
"""

import sys

from app.agent import run_cli
from app.config import ConfigurationError, Settings


def main() -> None:
    if len(sys.argv) > 1:
        run_cli()
        return

    try:
        settings = Settings.from_env()
    except ConfigurationError as exc:
        raise SystemExit(f"Configuration error: {exc}") from exc

    print("Meridian chatbot — pass a question as argv to run the agent, or use Stage 13 UI.")
    print(f"MCP server: {settings.mcp_server_url}")
    print(f"Model: {settings.model_name}")


if __name__ == "__main__":
    main()
