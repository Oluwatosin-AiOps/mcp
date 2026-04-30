"""Environment-backed settings with validation."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse

from dotenv import load_dotenv


class ConfigurationError(ValueError):
    """Raised when required settings are missing or invalid."""


def load_dotenv_safe() -> None:
    """Load `.env` from the current working directory without overriding existing OS env."""
    load_dotenv(override=False)


@dataclass(frozen=True)
class Settings:
    """Application configuration drawn from the environment."""

    mcp_server_url: str
    openai_api_key: str
    model_name: str

    @classmethod
    def from_env(cls, *, require_openai_key: bool = True) -> Settings:
        """
        Read settings from the environment.

        Use ``require_openai_key=False`` for MCP-only utilities (e.g. tool discovery)
        where the OpenAI key is not used.
        """
        load_dotenv_safe()

        mcp_url = os.getenv("MCP_SERVER_URL", "").strip()
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        model_name = os.getenv("MODEL_NAME", "gpt-4o-mini").strip()

        errors: list[str] = []
        if not mcp_url:
            errors.append("MCP_SERVER_URL is required")
        else:
            parsed = urlparse(mcp_url)
            if parsed.scheme not in ("http", "https"):
                errors.append("MCP_SERVER_URL must start with http:// or https://")
            if not parsed.netloc:
                errors.append("MCP_SERVER_URL must include a host")

        if require_openai_key and not api_key:
            errors.append("OPENAI_API_KEY is required")

        if not model_name:
            errors.append("MODEL_NAME must not be empty")

        if errors:
            raise ConfigurationError("; ".join(errors))

        return cls(
            mcp_server_url=mcp_url,
            openai_api_key=api_key,
            model_name=model_name,
        )
