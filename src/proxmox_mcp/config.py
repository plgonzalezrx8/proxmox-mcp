"""Configuration for Proxmox MCP."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse


def _env_bool(name: str, default: bool = True) -> bool:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


def _normalize_base_url(raw: str) -> str:
    value = raw.strip().rstrip("/")
    if value.endswith("/api2/json"):
        value = value[: -len("/api2/json")]
    if not value:
        raise ValueError("PVE_BASE_URL is required")
    parsed = urlparse(value)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        raise ValueError("PVE_BASE_URL must be an absolute http(s) URL")
    if parsed.query or parsed.fragment:
        raise ValueError("PVE_BASE_URL must not include query strings or fragments")
    if parsed.path not in {"", "/"}:
        raise ValueError("PVE_BASE_URL must point to the Proxmox origin, not an API subpath")
    if parsed.scheme == "http" and not _env_bool("PVE_ALLOW_INSECURE_HTTP", False):
        raise ValueError("PVE_BASE_URL must use https unless PVE_ALLOW_INSECURE_HTTP=true")
    return value


@dataclass(frozen=True)
class ProxmoxConfig:
    """Runtime configuration for Proxmox API access."""

    base_url: str
    api_token_id: str | None = None
    api_token_secret: str | None = None
    username: str | None = None
    password: str | None = None
    verify_ssl: bool = True
    timeout: float = 30.0

    @property
    def api_base_url(self) -> str:
        return f"{self.base_url}/api2/json"

    @property
    def has_api_token(self) -> bool:
        return bool(self.api_token_id and self.api_token_secret)

    @property
    def has_password_auth(self) -> bool:
        return bool(self.username and self.password)

    @classmethod
    def from_env(cls) -> ProxmoxConfig:
        base_url = _normalize_base_url(os.getenv("PVE_BASE_URL", ""))
        cfg = cls(
            base_url=base_url,
            api_token_id=os.getenv("PVE_API_TOKEN_ID") or None,
            api_token_secret=os.getenv("PVE_API_TOKEN_SECRET") or None,
            username=os.getenv("PVE_USERNAME") or None,
            password=os.getenv("PVE_PASSWORD") or None,
            verify_ssl=_env_bool("PVE_VERIFY_SSL", True),
            timeout=float(os.getenv("PVE_TIMEOUT", "30")),
        )
        if not (cfg.has_api_token or cfg.has_password_auth):
            raise ValueError("Proxmox config requires API token or username/password credentials")
        return cfg
