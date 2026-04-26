from __future__ import annotations

import pytest

from proxmox_mcp.config import ProxmoxConfig


def test_config_normalizes_api2_json_url(monkeypatch):
    monkeypatch.setenv("PVE_BASE_URL", "https://proxmox.lan:8006/api2/json/")
    monkeypatch.setenv("PVE_API_TOKEN_ID", "root@pam!mcp")
    monkeypatch.setenv("PVE_API_TOKEN_SECRET", "secret")
    monkeypatch.setenv("PVE_VERIFY_SSL", "false")

    cfg = ProxmoxConfig.from_env()

    assert cfg.base_url == "https://proxmox.lan:8006"
    assert cfg.api_base_url == "https://proxmox.lan:8006/api2/json"
    assert cfg.verify_ssl is False
    assert cfg.api_token_id == "root@pam!mcp"


def test_config_requires_token_or_password(monkeypatch):
    monkeypatch.setenv("PVE_BASE_URL", "https://proxmox.lan:8006")
    monkeypatch.delenv("PVE_API_TOKEN_ID", raising=False)
    monkeypatch.delenv("PVE_API_TOKEN_SECRET", raising=False)
    monkeypatch.delenv("PVE_USERNAME", raising=False)
    monkeypatch.delenv("PVE_PASSWORD", raising=False)

    with pytest.raises(ValueError, match="API token or username/password"):
        ProxmoxConfig.from_env()


def test_config_rejects_insecure_http_unless_explicitly_allowed(monkeypatch):
    monkeypatch.setenv("PVE_BASE_URL", "http://proxmox.lan:8006")
    monkeypatch.setenv("PVE_API_TOKEN_ID", "root@pam!mcp")
    monkeypatch.setenv("PVE_API_TOKEN_SECRET", "secret")
    monkeypatch.delenv("PVE_ALLOW_INSECURE_HTTP", raising=False)

    with pytest.raises(ValueError, match="https"):
        ProxmoxConfig.from_env()

    monkeypatch.setenv("PVE_ALLOW_INSECURE_HTTP", "true")
    assert ProxmoxConfig.from_env().base_url == "http://proxmox.lan:8006"


def test_config_rejects_base_url_with_query_or_fragment(monkeypatch):
    monkeypatch.setenv("PVE_BASE_URL", "https://proxmox.lan:8006?token=oops")
    monkeypatch.setenv("PVE_API_TOKEN_ID", "root@pam!mcp")
    monkeypatch.setenv("PVE_API_TOKEN_SECRET", "secret")

    with pytest.raises(ValueError, match="must not include query"):
        ProxmoxConfig.from_env()
