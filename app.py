"""
Hugging Face Spaces / local entrypoint for the Gradio UI.

Stage 0: stub. Stage 13 will mount the real chat interface from app.ui.
"""

from app.config import ConfigurationError, Settings


def main() -> None:
    try:
        settings = Settings.from_env()
    except ConfigurationError as exc:
        raise SystemExit(f"Configuration error: {exc}") from exc

    print("Meridian chatbot — UI wiring lands in Stage 13.")
    print(f"MCP server: {settings.mcp_server_url}")
    print(f"Model: {settings.model_name}")


if __name__ == "__main__":
    main()
