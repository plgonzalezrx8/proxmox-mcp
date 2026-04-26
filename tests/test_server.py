from __future__ import annotations

from proxmox_mcp.server import EXPECTED_TOOL_NAMES, create_server


def test_server_imports_and_declares_expected_tools():
    server = create_server()

    assert server is not None
    assert "pve_get_version" in EXPECTED_TOOL_NAMES
    assert "pve_api_request" in EXPECTED_TOOL_NAMES
    assert len(EXPECTED_TOOL_NAMES) >= 25
