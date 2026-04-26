"""HTTP client for the Proxmox VE API."""

from __future__ import annotations

from typing import Any

import httpx

from .config import ProxmoxConfig
from .safety import normalize_api_path

SENSITIVE_KEYS = {"authorization", "cookie", "csrfpreventiontoken", "password", "token", "secret", "ticket"}


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "***REDACTED***" if any(part in str(key).lower() for part in SENSITIVE_KEYS) else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


class ProxmoxApiError(RuntimeError):
    """Raised when Proxmox returns an HTTP error."""

    def __init__(self, status_code: int, payload: Any):
        self.status_code = status_code
        self.payload = _redact(payload)
        super().__init__(f"Proxmox API error {status_code}: {self.payload}")


class ProxmoxClient:
    """Small Proxmox API client with API-token and ticket auth support."""

    def __init__(self, config: ProxmoxConfig, *, transport: httpx.BaseTransport | None = None):
        self.config = config
        self._ticket: str | None = None
        self._csrf: str | None = None
        self._client = httpx.Client(
            verify=config.verify_ssl,
            timeout=config.timeout,
            transport=transport,
            headers={"Accept": "application/json"},
        )

    def close(self) -> None:
        self._client.close()

    def _url(self, path: str) -> str:
        return f"{self.config.api_base_url}{normalize_api_path(path)}"

    def _headers(self, method: str) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.config.has_api_token:
            headers["Authorization"] = f"PVEAPIToken={self.config.api_token_id}={self.config.api_token_secret}"
        elif self._ticket:
            headers["Cookie"] = f"PVEAuthCookie={self._ticket}"
            if method.upper() != "GET" and self._csrf:
                headers["CSRFPreventionToken"] = self._csrf
        return headers

    def authenticate(self) -> None:
        """Fetch a ticket and CSRF token for username/password auth."""
        if self.config.has_api_token or self._ticket:
            return
        if not self.config.has_password_auth:
            raise ValueError("No username/password credentials configured")
        response = self._client.post(
            self._url("/access/ticket"),
            data={"username": self.config.username, "password": self.config.password},
        )
        payload = self._decode_response(response)
        data = payload.get("data", {}) if isinstance(payload, dict) else {}
        self._ticket = data.get("ticket")
        self._csrf = data.get("CSRFPreventionToken")
        if not self._ticket:
            raise ProxmoxApiError(response.status_code, payload)

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        method_upper = method.upper()
        if not self.config.has_api_token:
            self.authenticate()
        kwargs: dict[str, Any] = {"headers": self._headers(method_upper)}
        if method_upper == "GET":
            kwargs["params"] = params
        else:
            kwargs["data"] = params
        response = self._client.request(method_upper, self._url(path), **kwargs)
        return self._decode_response(response)

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("GET", path, params)

    def post(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("POST", path, params)

    def put(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("PUT", path, params)

    def delete(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("DELETE", path, params)

    @staticmethod
    def _decode_response(response: httpx.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError:
            payload = {"message": response.text}
        if response.status_code >= 400:
            raise ProxmoxApiError(response.status_code, payload)
        if not isinstance(payload, dict):
            return {"data": payload}
        return payload
