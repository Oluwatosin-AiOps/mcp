"""Entrypoint: Gradio (no args), --print-config, or CLI agent turn."""

import sys

from app.agent import run_cli
from app.config import ConfigurationError, Settings


def _print_config() -> None:
    try:
        settings = Settings.from_env()
    except ConfigurationError as exc:
        raise SystemExit(f"Configuration error: {exc}") from exc
    print("Meridian chatbot — configuration")
    print(f"MCP server: {settings.mcp_server_url}")
    print(f"Model: {settings.model_name}")
    print("Launch UI: uv run python app.py")
    print('CLI one-shot: uv run python app.py "Your question here"')


def main() -> None:
    argv = sys.argv[1:]
    if not argv:
        from app.ui import launch_ui

        launch_ui()
        return

    if argv[0] in ("--print-config", "--config", "-c"):
        _print_config()
        return

    run_cli()


if __name__ == "__main__":
    main()
