from __future__ import annotations

import pytest

from proxmox_mcp.safety import ConfirmationRequired
from proxmox_mcp.tools import ProxmoxTools


def test_lifecycle_tools_require_confirmation(fake_client):
    tools = ProxmoxTools(fake_client)

    with pytest.raises(ConfirmationRequired):
        tools.stop_vm("pve", 100)

    assert fake_client.calls == []


def test_lifecycle_tools_call_status_endpoints(fake_client):
    tools = ProxmoxTools(fake_client)

    tools.start_vm("pve", 100, confirm=True)
    tools.shutdown_vm("pve", 100, confirm=True, timeout=60)
    tools.stop_vm("pve", 100, confirm=True)
    tools.reboot_vm("pve", 100, confirm=True)
    tools.suspend_vm("pve", 100, confirm=True)
    tools.resume_vm("pve", 100, confirm=True)

    assert fake_client.calls == [
        ("POST", "/nodes/pve/qemu/100/status/start", None),
        ("POST", "/nodes/pve/qemu/100/status/shutdown", {"timeout": 60}),
        ("POST", "/nodes/pve/qemu/100/status/stop", None),
        ("POST", "/nodes/pve/qemu/100/status/reboot", None),
        ("POST", "/nodes/pve/qemu/100/status/suspend", None),
        ("POST", "/nodes/pve/qemu/100/status/resume", None),
    ]


def test_snapshot_and_migration_tools(fake_client):
    tools = ProxmoxTools(fake_client)

    tools.create_snapshot("pve", 100, "pre-upgrade", description="safe point", confirm=True)
    tools.delete_snapshot("pve", 100, "old", confirm=True)
    tools.rollback_snapshot("pve", 100, "pre-upgrade", confirm=True)
    tools.migrate_vm("pve", 100, "pve2", online=True, confirm=True)

    assert fake_client.calls == [
        ("POST", "/nodes/pve/qemu/100/snapshot", {"snapname": "pre-upgrade", "description": "safe point"}),
        ("DELETE", "/nodes/pve/qemu/100/snapshot/old", None),
        ("POST", "/nodes/pve/qemu/100/snapshot/pre-upgrade/rollback", None),
        ("POST", "/nodes/pve/qemu/100/migrate", {"target": "pve2", "online": 1}),
    ]
