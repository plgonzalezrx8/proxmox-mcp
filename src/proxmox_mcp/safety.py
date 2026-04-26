"""Safety gates and path validation for Proxmox API calls."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote, unquote, urlparse

READ_ONLY_METHODS = {"GET"}
MUTATING_METHODS = {"POST", "PUT", "DELETE"}


class ConfirmationRequired(PermissionError):
    """Raised when a mutating Proxmox operation lacks explicit confirmation."""


def _has_control_chars(value: str) -> bool:
    return any(ord(ch) < 32 or ord(ch) == 127 for ch in value)


def confirm_mutation(method: str, path: str, *, confirm: bool = False) -> None:
    """Require explicit confirmation for non-GET requests."""
    method_upper = method.upper()
    if method_upper in READ_ONLY_METHODS:
        return
    if method_upper not in MUTATING_METHODS:
        raise ValueError(f"Unsupported HTTP method for Proxmox API: {method}")
    if not confirm:
        raise ConfirmationRequired(f"{method_upper} {path} changes Proxmox state and requires confirm=true")


def normalize_api_path(path: str) -> str:
    """Normalize a Proxmox API path and reject unsafe path forms."""
    raw = (path or "").strip()
    if not raw:
        raise ValueError("API path is required")
    if _has_control_chars(raw):
        raise ValueError("API path must not contain control characters")
    parsed = urlparse(raw)
    if parsed.scheme or parsed.netloc:
        raise ValueError("Use an API path like /nodes, not a full URL")
    if parsed.query or parsed.fragment:
        raise ValueError("API path must not include query strings or fragments; pass params separately")
    decoded = unquote(raw)
    if _has_control_chars(decoded):
        raise ValueError("API path must not contain encoded control characters")
    if not raw.startswith("/"):
        raw = f"/{raw}"
        decoded = f"/{decoded}"
    if raw.startswith("/api2/json"):
        raw = raw[len("/api2/json") :] or "/"
        decoded = decoded[len("/api2/json") :] or "/"
    raw_segments = raw.split("/")
    decoded_segments = decoded.split("/")
    if "" in raw_segments[1:] or "" in decoded_segments[1:]:
        raise ValueError("API path must not contain empty or encoded slash segments")
    if ".." in raw_segments or ".." in decoded_segments:
        raise ValueError("API path traversal is not allowed")
    return raw


def api_segment(value: Any, name: str = "path segment") -> str:
    """Validate and URL-encode one API path segment."""
    text = str(value).strip()
    decoded = unquote(text)
    if not text:
        raise ValueError(f"{name} is required")
    if _has_control_chars(text) or _has_control_chars(decoded):
        raise ValueError(f"{name} must not contain control characters")
    if decoded in {".", ".."} or "/" in decoded or "?" in decoded or "#" in decoded:
        raise ValueError(f"{name} contains unsafe path characters")
    return quote(decoded, safe=":@._+-")


def api_path(*segments: Any) -> str:
    """Join validated path segments into an API path."""
    return "/" + "/".join(api_segment(segment) for segment in segments)


def vm_kind(vm_type: str) -> str:
    """Validate Proxmox guest type."""
    if vm_type not in {"qemu", "lxc"}:
        raise ValueError("vm_type must be 'qemu' or 'lxc'")
    return vm_type


def bool_param(value: bool | None) -> int | None:
    if value is None:
        return None
    return 1 if value else 0


def compact_params(params: dict | None) -> dict | None:
    """Drop None values while preserving falsey useful values like 0/False/empty strings."""
    if not params:
        return None
    compacted = {key: value for key, value in params.items() if value is not None}
    return compacted or None
