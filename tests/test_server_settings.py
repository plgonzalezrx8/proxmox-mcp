from __future__ import annotations

import pytest

from proxmox_mcp.server import ServerSettings


def test_server_settings_default_to_streamable_http_for_containers(monkeypatch):
    monkeypatch.delenv("MCP_TRANSPORT", raising=False)
    monkeypatch.delenv("MCP_HOST", raising=False)
    monkeypatch.delenv("MCP_PORT", raising=False)
    monkeypatch.delenv("MCP_PATH", raising=False)

    settings = ServerSettings.from_env()

    assert settings.transport == "streamable-http"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert settings.mount_path == "/mcp"


def test_server_settings_support_stdio_sse_and_streamable_http(monkeypatch):
    for transport in ["stdio", "sse", "streamable-http"]:
        monkeypatch.setenv("MCP_TRANSPORT", transport)
        assert ServerSettings.from_env().transport == transport


def test_server_settings_reject_bad_transport(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "websocket")

    with pytest.raises(ValueError, match="MCP_TRANSPORT"):
        ServerSettings.from_env()


def test_server_settings_reject_bad_mount_path(monkeypatch):
    monkeypatch.setenv("MCP_PATH", "mcp")

    with pytest.raises(ValueError, match="MCP_PATH"):
        ServerSettings.from_env()

    monkeypatch.setenv("MCP_PATH", "/mcp?x=y")
    with pytest.raises(ValueError, match="MCP_PATH"):
        ServerSettings.from_env()
