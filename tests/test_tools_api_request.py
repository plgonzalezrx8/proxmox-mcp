from __future__ import annotations

import pytest

from proxmox_mcp.safety import ConfirmationRequired
from proxmox_mcp.tools import ProxmoxTools


def test_generic_api_get_without_confirmation(fake_client):
    tools = ProxmoxTools(fake_client)

    tools.api_request("GET", "/nodes", {"foo": "bar"})

    assert fake_client.calls == [("GET", "/nodes", {"foo": "bar"})]


def test_generic_api_mutation_requires_confirmation(fake_client):
    tools = ProxmoxTools(fake_client)

    with pytest.raises(ConfirmationRequired):
        tools.api_request("POST", "/nodes/pve/qemu/100/status/stop")


def test_generic_api_mutation_with_confirmation(fake_client):
    tools = ProxmoxTools(fake_client)

    tools.api_request("POST", "/api2/json/nodes/pve/qemu/100/status/start", confirm=True)

    assert fake_client.calls == [("POST", "/nodes/pve/qemu/100/status/start", None)]


def test_tool_rejects_invalid_vm_type(fake_client):
    tools = ProxmoxTools(fake_client)

    with pytest.raises(ValueError):
        tools.get_vm_status("pve", 100, "../../access")  # type: ignore[arg-type]
