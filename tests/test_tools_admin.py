from __future__ import annotations

import pytest

from proxmox_mcp.safety import ConfirmationRequired
from proxmox_mcp.tools import ProxmoxTools


def test_admin_tools_require_confirmation(fake_client):
    tools = ProxmoxTools(fake_client)

    with pytest.raises(ConfirmationRequired):
        tools.delete_vm("pve", 100)


def test_admin_tools_call_expected_endpoints(fake_client):
    tools = ProxmoxTools(fake_client)

    tools.clone_vm("pve", 100, 200, name="clone", full=True, confirm=True)
    tools.create_lxc("pve", 201, "local:vztmpl/debian.tar.zst", "local-lvm", hostname="ct", confirm=True)
    tools.create_qemu_vm("pve", 202, name="vm", memory=4096, cores=2, confirm=True)
    tools.delete_vm("pve", 203, vm_type="lxc", purge=True, confirm=True)
    tools.resize_disk("pve", 202, "scsi0", "+10G", confirm=True)
    tools.set_vm_config("pve", 202, {"memory": 8192}, confirm=True)

    assert fake_client.calls == [
        ("POST", "/nodes/pve/qemu/100/clone", {"newid": 200, "name": "clone", "full": 1}),
        ("POST", "/nodes/pve/lxc", {"vmid": 201, "ostemplate": "local:vztmpl/debian.tar.zst", "storage": "local-lvm", "hostname": "ct"}),
        ("POST", "/nodes/pve/qemu", {"vmid": 202, "name": "vm", "memory": 4096, "cores": 2}),
        ("DELETE", "/nodes/pve/lxc/203", {"purge": 1}),
        ("PUT", "/nodes/pve/qemu/202/resize", {"disk": "scsi0", "size": "+10G"}),
        ("PUT", "/nodes/pve/qemu/202/config", {"memory": 8192}),
    ]
