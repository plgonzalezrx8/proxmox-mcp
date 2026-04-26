"""MCP server entrypoint for Proxmox VE."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from mcp.server.fastmcp import FastMCP

from .tools import ProxmoxTools

EXPECTED_TOOL_NAMES = [
    "pve_get_version",
    "pve_get_cluster_status",
    "pve_list_nodes",
    "pve_list_resources",
    "pve_list_vms",
    "pve_get_vm_status",
    "pve_get_vm_config",
    "pve_list_storage",
    "pve_list_backups",
    "pve_get_task_status",
    "pve_get_node_metrics",
    "pve_start_vm",
    "pve_shutdown_vm",
    "pve_stop_vm",
    "pve_reboot_vm",
    "pve_suspend_vm",
    "pve_resume_vm",
    "pve_create_snapshot",
    "pve_delete_snapshot",
    "pve_rollback_snapshot",
    "pve_migrate_vm",
    "pve_clone_vm",
    "pve_create_lxc",
    "pve_create_qemu_vm",
    "pve_delete_vm",
    "pve_resize_disk",
    "pve_set_vm_config",
    "pve_api_request",
]


@lru_cache(maxsize=1)
def _tools() -> ProxmoxTools:
    return ProxmoxTools()


def create_server() -> FastMCP:
    """Create and configure the Proxmox MCP server."""
    mcp = FastMCP("proxmox-mcp")

    @mcp.tool(name="pve_get_version")
    def pve_get_version() -> dict[str, Any]:
        """Return Proxmox VE version information."""
        return _tools().get_version()

    @mcp.tool(name="pve_get_cluster_status")
    def pve_get_cluster_status() -> dict[str, Any]:
        """Return Proxmox cluster status."""
        return _tools().get_cluster_status()

    @mcp.tool(name="pve_list_nodes")
    def pve_list_nodes() -> dict[str, Any]:
        """List Proxmox nodes."""
        return _tools().list_nodes()

    @mcp.tool(name="pve_list_resources")
    def pve_list_resources(resource_type: str | None = None) -> dict[str, Any]:
        """List cluster resources, optionally filtered by type such as vm, storage, node."""
        return _tools().list_resources(resource_type)

    @mcp.tool(name="pve_list_vms")
    def pve_list_vms() -> dict[str, Any]:
        """List QEMU VMs and LXC containers from cluster resources."""
        return _tools().list_vms()

    @mcp.tool(name="pve_get_vm_status")
    def pve_get_vm_status(node: str, vmid: int, vm_type: str = "qemu") -> dict[str, Any]:
        """Get current status for a QEMU VM or LXC container."""
        return _tools().get_vm_status(node, vmid, vm_type)  # type: ignore[arg-type]

    @mcp.tool(name="pve_get_vm_config")
    def pve_get_vm_config(node: str, vmid: int, vm_type: str = "qemu") -> dict[str, Any]:
        """Get config for a QEMU VM or LXC container."""
        return _tools().get_vm_config(node, vmid, vm_type)  # type: ignore[arg-type]

    @mcp.tool(name="pve_list_storage")
    def pve_list_storage(node: str | None = None) -> dict[str, Any]:
        """List storage globally or for a node."""
        return _tools().list_storage(node)

    @mcp.tool(name="pve_list_backups")
    def pve_list_backups(node: str, storage: str) -> dict[str, Any]:
        """List backup content for a node storage."""
        return _tools().list_backups(node, storage)

    @mcp.tool(name="pve_get_task_status")
    def pve_get_task_status(node: str, upid: str) -> dict[str, Any]:
        """Get task status by UPID."""
        return _tools().get_task_status(node, upid)

    @mcp.tool(name="pve_get_node_metrics")
    def pve_get_node_metrics(node: str) -> dict[str, Any]:
        """Get node status and metrics."""
        return _tools().get_node_metrics(node)

    @mcp.tool(name="pve_start_vm")
    def pve_start_vm(node: str, vmid: int, vm_type: str = "qemu", confirm: bool = False) -> dict[str, Any]:
        """Start a VM/container. Requires confirm=true."""
        return _tools().start_vm(node, vmid, vm_type, confirm=confirm)  # type: ignore[arg-type]

    @mcp.tool(name="pve_shutdown_vm")
    def pve_shutdown_vm(
        node: str,
        vmid: int,
        vm_type: str = "qemu",
        timeout: int | None = None,
        force_stop: bool | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Gracefully shut down a VM/container. Requires confirm=true."""
        return _tools().shutdown_vm(node, vmid, vm_type, timeout=timeout, force_stop=force_stop, confirm=confirm)  # type: ignore[arg-type]

    @mcp.tool(name="pve_stop_vm")
    def pve_stop_vm(node: str, vmid: int, vm_type: str = "qemu", confirm: bool = False) -> dict[str, Any]:
        """Hard stop a VM/container. Requires confirm=true."""
        return _tools().stop_vm(node, vmid, vm_type, confirm=confirm)  # type: ignore[arg-type]

    @mcp.tool(name="pve_reboot_vm")
    def pve_reboot_vm(node: str, vmid: int, vm_type: str = "qemu", confirm: bool = False) -> dict[str, Any]:
        """Reboot a VM/container. Requires confirm=true."""
        return _tools().reboot_vm(node, vmid, vm_type, confirm=confirm)  # type: ignore[arg-type]

    @mcp.tool(name="pve_suspend_vm")
    def pve_suspend_vm(node: str, vmid: int, vm_type: str = "qemu", confirm: bool = False) -> dict[str, Any]:
        """Suspend a VM/container. Requires confirm=true."""
        return _tools().suspend_vm(node, vmid, vm_type, confirm=confirm)  # type: ignore[arg-type]

    @mcp.tool(name="pve_resume_vm")
    def pve_resume_vm(node: str, vmid: int, vm_type: str = "qemu", confirm: bool = False) -> dict[str, Any]:
        """Resume a VM/container. Requires confirm=true."""
        return _tools().resume_vm(node, vmid, vm_type, confirm=confirm)  # type: ignore[arg-type]

    @mcp.tool(name="pve_create_snapshot")
    def pve_create_snapshot(
        node: str,
        vmid: int,
        snapname: str,
        vm_type: str = "qemu",
        description: str | None = None,
        vmstate: bool | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Create a VM/container snapshot. Requires confirm=true."""
        return _tools().create_snapshot(node, vmid, snapname, vm_type, description=description, vmstate=vmstate, confirm=confirm)  # type: ignore[arg-type]

    @mcp.tool(name="pve_delete_snapshot")
    def pve_delete_snapshot(node: str, vmid: int, snapname: str, vm_type: str = "qemu", confirm: bool = False) -> dict[str, Any]:
        """Delete a VM/container snapshot. Requires confirm=true."""
        return _tools().delete_snapshot(node, vmid, snapname, vm_type, confirm=confirm)  # type: ignore[arg-type]

    @mcp.tool(name="pve_rollback_snapshot")
    def pve_rollback_snapshot(node: str, vmid: int, snapname: str, vm_type: str = "qemu", confirm: bool = False) -> dict[str, Any]:
        """Rollback to a snapshot. Requires confirm=true."""
        return _tools().rollback_snapshot(node, vmid, snapname, vm_type, confirm=confirm)  # type: ignore[arg-type]

    @mcp.tool(name="pve_migrate_vm")
    def pve_migrate_vm(
        node: str,
        vmid: int,
        target: str,
        vm_type: str = "qemu",
        online: bool | None = None,
        with_local_disks: bool | None = None,
        targetstorage: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Migrate a VM/container to another node. Requires confirm=true."""
        return _tools().migrate_vm(
            node,
            vmid,
            target,
            vm_type,
            online=online,
            with_local_disks=with_local_disks,
            targetstorage=targetstorage,
            confirm=confirm,
        )  # type: ignore[arg-type]

    @mcp.tool(name="pve_clone_vm")
    def pve_clone_vm(
        node: str,
        source_vmid: int,
        newid: int,
        name: str | None = None,
        full: bool | None = None,
        target: str | None = None,
        storage: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Clone a QEMU VM. Requires confirm=true."""
        return _tools().clone_vm(node, source_vmid, newid, name=name, full=full, target=target, storage=storage, confirm=confirm)

    @mcp.tool(name="pve_create_lxc")
    def pve_create_lxc(
        node: str,
        vmid: int,
        ostemplate: str,
        storage: str,
        hostname: str | None = None,
        memory: int | None = None,
        cores: int | None = None,
        net0: str | None = None,
        rootfs: str | None = None,
        password: str | None = None,
        ssh_public_keys: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Create an LXC container. Requires confirm=true."""
        return _tools().create_lxc(
            node,
            vmid,
            ostemplate,
            storage,
            hostname=hostname,
            memory=memory,
            cores=cores,
            net0=net0,
            rootfs=rootfs,
            password=password,
            ssh_public_keys=ssh_public_keys,
            confirm=confirm,
        )

    @mcp.tool(name="pve_create_qemu_vm")
    def pve_create_qemu_vm(
        node: str,
        vmid: int,
        name: str | None = None,
        memory: int | None = None,
        cores: int | None = None,
        sockets: int | None = None,
        net0: str | None = None,
        scsi0: str | None = None,
        ide2: str | None = None,
        ostype: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Create a QEMU VM. Requires confirm=true."""
        return _tools().create_qemu_vm(
            node,
            vmid,
            name=name,
            memory=memory,
            cores=cores,
            sockets=sockets,
            net0=net0,
            scsi0=scsi0,
            ide2=ide2,
            ostype=ostype,
            confirm=confirm,
        )

    @mcp.tool(name="pve_delete_vm")
    def pve_delete_vm(
        node: str,
        vmid: int,
        vm_type: str = "qemu",
        purge: bool | None = None,
        destroy_unreferenced_disks: bool | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Delete a VM/container. Requires confirm=true."""
        return _tools().delete_vm(
            node,
            vmid,
            vm_type,
            purge=purge,
            destroy_unreferenced_disks=destroy_unreferenced_disks,
            confirm=confirm,
        )  # type: ignore[arg-type]

    @mcp.tool(name="pve_resize_disk")
    def pve_resize_disk(node: str, vmid: int, disk: str, size: str, confirm: bool = False) -> dict[str, Any]:
        """Resize a QEMU VM disk. Requires confirm=true."""
        return _tools().resize_disk(node, vmid, disk, size, confirm=confirm)

    @mcp.tool(name="pve_set_vm_config")
    def pve_set_vm_config(node: str, vmid: int, config: dict[str, Any], vm_type: str = "qemu", confirm: bool = False) -> dict[str, Any]:
        """Update VM/container config. Requires confirm=true."""
        return _tools().set_vm_config(node, vmid, config, vm_type, confirm=confirm)  # type: ignore[arg-type]

    @mcp.tool(name="pve_api_request")
    def pve_api_request(method: str, path: str, params: dict[str, Any] | None = None, confirm: bool = False) -> dict[str, Any]:
        """Call any Proxmox API path. GET is allowed; POST/PUT/DELETE require confirm=true."""
        return _tools().api_request(method, path, params, confirm=confirm)

    return mcp


app = create_server()


def main() -> None:
    """Run the stdio MCP server."""
    app.run()


if __name__ == "__main__":
    main()
