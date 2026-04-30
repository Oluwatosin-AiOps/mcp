import pytest

from app.config import ConfigurationError, Settings


def test_from_env_success(monkeypatch):
    monkeypatch.setenv("MCP_SERVER_URL", "https://example.com/mcp")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("MODEL_NAME", "gpt-4o-mini")
    s = Settings.from_env(load_env_file=False)
    assert s.mcp_server_url == "https://example.com/mcp"
    assert s.openai_api_key == "sk-test"
    assert s.model_name == "gpt-4o-mini"


def test_default_model_name(monkeypatch):
    monkeypatch.setenv("MCP_SERVER_URL", "https://example.com/mcp")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.delenv("MODEL_NAME", raising=False)
    s = Settings.from_env(load_env_file=False)
    assert s.model_name == "gpt-4o-mini"


def test_missing_mcp_url(monkeypatch):
    monkeypatch.delenv("MCP_SERVER_URL", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    with pytest.raises(ConfigurationError, match="MCP_SERVER_URL"):
        Settings.from_env(load_env_file=False)


def test_invalid_mcp_scheme(monkeypatch):
    monkeypatch.setenv("MCP_SERVER_URL", "ftp://example.com/mcp")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    with pytest.raises(ConfigurationError, match="http"):
        Settings.from_env(load_env_file=False)


def test_missing_openai_key(monkeypatch):
    monkeypatch.setenv("MCP_SERVER_URL", "https://example.com/mcp")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
        Settings.from_env(load_env_file=False)


def test_openai_key_optional(monkeypatch):
    monkeypatch.setenv("MCP_SERVER_URL", "https://example.com/mcp")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    s = Settings.from_env(require_openai_key=False, load_env_file=False)
    assert s.openai_api_key == ""
