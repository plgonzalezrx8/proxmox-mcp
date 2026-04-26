from __future__ import annotations

import pytest

from proxmox_mcp.safety import (
    ConfirmationRequired,
    api_path,
    api_segment,
    confirm_mutation,
    normalize_api_path,
)


def test_get_does_not_require_confirmation():
    confirm_mutation("GET", "/nodes", confirm=False)


def test_post_requires_confirmation():
    with pytest.raises(ConfirmationRequired):
        confirm_mutation("POST", "/nodes/pve/qemu/100/status/stop", confirm=False)


def test_delete_with_confirmation_is_allowed():
    confirm_mutation("DELETE", "/nodes/pve/qemu/100", confirm=True)


def test_normalize_api_path_rejects_full_urls_and_traversal():
    with pytest.raises(ValueError):
        normalize_api_path("https://proxmox.lan:8006/api2/json/nodes")
    with pytest.raises(ValueError):
        normalize_api_path("/nodes/../access")


def test_normalize_api_path_rejects_query_fragment_and_encoded_traversal():
    for path in ["/nodes?x=y", "/nodes#frag", "/nodes/%2e%2e/access", "/nodes/%2Faccess"]:
        with pytest.raises(ValueError):
            normalize_api_path(path)


def test_normalize_api_path_strips_api_prefix():
    assert normalize_api_path("/api2/json/nodes") == "/nodes"
    assert normalize_api_path("nodes/pve") == "/nodes/pve"


def test_api_segment_rejects_path_breakout_characters():
    for value in ["pve/foo", "pve?x=y", "pve#frag", "..", "%2e%2e", "bad\nnode"]:
        with pytest.raises(ValueError):
            api_segment(value, "node")


def test_api_path_joins_safe_segments():
    assert api_path("nodes", "pve", "qemu", 100, "status", "current") == "/nodes/pve/qemu/100/status/current"
