from __future__ import annotations

from proxmox_mcp.tools import ProxmoxTools


def test_readonly_cluster_tools(fake_client):
    tools = ProxmoxTools(fake_client)

    tools.get_version()
    tools.get_cluster_status()
    tools.list_nodes()
    tools.list_resources(resource_type="vm")

    assert fake_client.calls == [
        ("GET", "/version", None),
        ("GET", "/cluster/status", None),
        ("GET", "/nodes", None),
        ("GET", "/cluster/resources", {"type": "vm"}),
    ]


def test_readonly_vm_storage_backup_task_metric_tools(fake_client):
    tools = ProxmoxTools(fake_client)

    tools.list_vms()
    tools.get_vm_status("pve", 100, "qemu")
    tools.get_vm_config("pve", 101, "lxc")
    tools.list_storage("pve")
    tools.list_backups("pve", "local")
    tools.get_task_status("pve", "UPID:pve:abc")
    tools.get_node_metrics("pve")

    assert fake_client.calls == [
        ("GET", "/cluster/resources", {"type": "vm"}),
        ("GET", "/nodes/pve/qemu/100/status/current", None),
        ("GET", "/nodes/pve/lxc/101/config", None),
        ("GET", "/nodes/pve/storage", None),
        ("GET", "/nodes/pve/storage/local/content", {"content": "backup"}),
        ("GET", "/nodes/pve/tasks/UPID:pve:abc/status", None),
        ("GET", "/nodes/pve/status", None),
    ]
