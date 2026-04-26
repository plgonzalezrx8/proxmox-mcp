"""High-level Proxmox MCP tool implementations."""

from __future__ import annotations

from typing import Any, Literal

from .client import ProxmoxClient
from .config import ProxmoxConfig
from .safety import api_path, bool_param, compact_params, confirm_mutation, normalize_api_path, vm_kind

VmType = Literal["qemu", "lxc"]


class ProxmoxTools:
    """Curated Proxmox operations with explicit mutation confirmation."""

    def __init__(self, client: Any | None = None):
        self.client = client or ProxmoxClient(ProxmoxConfig.from_env())

    # Phase 1: read-only
    def get_version(self) -> dict[str, Any]:
        return self.client.get("/version")

    def get_cluster_status(self) -> dict[str, Any]:
        return self.client.get("/cluster/status")

    def list_nodes(self) -> dict[str, Any]:
        return self.client.get("/nodes")

    def list_resources(self, resource_type: str | None = None) -> dict[str, Any]:
        return self.client.get("/cluster/resources", compact_params({"type": resource_type}))

    def list_vms(self) -> dict[str, Any]:
        return self.list_resources(resource_type="vm")

    def get_vm_status(self, node: str, vmid: int, vm_type: VmType = "qemu") -> dict[str, Any]:
        return self.client.get(api_path("nodes", node, vm_kind(vm_type), vmid, "status", "current"))

    def get_vm_config(self, node: str, vmid: int, vm_type: VmType = "qemu") -> dict[str, Any]:
        return self.client.get(api_path("nodes", node, vm_kind(vm_type), vmid, "config"))

    def list_storage(self, node: str | None = None) -> dict[str, Any]:
        if node:
            return self.client.get(api_path("nodes", node, "storage"))
        return self.client.get("/storage")

    def list_backups(self, node: str, storage: str) -> dict[str, Any]:
        return self.client.get(api_path("nodes", node, "storage", storage, "content"), {"content": "backup"})

    def get_task_status(self, node: str, upid: str) -> dict[str, Any]:
        return self.client.get(api_path("nodes", node, "tasks", upid, "status"))

    def get_node_metrics(self, node: str) -> dict[str, Any]:
        return self.client.get(api_path("nodes", node, "status"))

    # Phase 2: safe actions
    def start_vm(self, node: str, vmid: int, vm_type: VmType = "qemu", *, confirm: bool = False):
        return self._post_confirmed(api_path("nodes", node, vm_kind(vm_type), vmid, "status", "start"), None, confirm)

    def shutdown_vm(
        self,
        node: str,
        vmid: int,
        vm_type: VmType = "qemu",
        *,
        timeout: int | None = None,
        force_stop: bool | None = None,
        confirm: bool = False,
    ):
        params = compact_params({"timeout": timeout, "forceStop": bool_param(force_stop)})
        return self._post_confirmed(api_path("nodes", node, vm_kind(vm_type), vmid, "status", "shutdown"), params, confirm)

    def stop_vm(self, node: str, vmid: int, vm_type: VmType = "qemu", *, confirm: bool = False):
        return self._post_confirmed(api_path("nodes", node, vm_kind(vm_type), vmid, "status", "stop"), None, confirm)

    def reboot_vm(self, node: str, vmid: int, vm_type: VmType = "qemu", *, confirm: bool = False):
        return self._post_confirmed(api_path("nodes", node, vm_kind(vm_type), vmid, "status", "reboot"), None, confirm)

    def suspend_vm(self, node: str, vmid: int, vm_type: VmType = "qemu", *, confirm: bool = False):
        return self._post_confirmed(api_path("nodes", node, vm_kind(vm_type), vmid, "status", "suspend"), None, confirm)

    def resume_vm(self, node: str, vmid: int, vm_type: VmType = "qemu", *, confirm: bool = False):
        return self._post_confirmed(api_path("nodes", node, vm_kind(vm_type), vmid, "status", "resume"), None, confirm)

    def create_snapshot(
        self,
        node: str,
        vmid: int,
        snapname: str,
        vm_type: VmType = "qemu",
        *,
        description: str | None = None,
        vmstate: bool | None = None,
        confirm: bool = False,
    ):
        params = compact_params({"snapname": snapname, "description": description, "vmstate": bool_param(vmstate)})
        return self._post_confirmed(api_path("nodes", node, vm_kind(vm_type), vmid, "snapshot"), params, confirm)

    def delete_snapshot(self, node: str, vmid: int, snapname: str, vm_type: VmType = "qemu", *, confirm: bool = False):
        return self._delete_confirmed(api_path("nodes", node, vm_kind(vm_type), vmid, "snapshot", snapname), None, confirm)

    def rollback_snapshot(self, node: str, vmid: int, snapname: str, vm_type: VmType = "qemu", *, confirm: bool = False):
        return self._post_confirmed(api_path("nodes", node, vm_kind(vm_type), vmid, "snapshot", snapname, "rollback"), None, confirm)

    def migrate_vm(
        self,
        node: str,
        vmid: int,
        target: str,
        vm_type: VmType = "qemu",
        *,
        online: bool | None = None,
        with_local_disks: bool | None = None,
        targetstorage: str | None = None,
        confirm: bool = False,
    ):
        params = compact_params(
            {
                "target": target,
                "online": bool_param(online),
                "with-local-disks": bool_param(with_local_disks),
                "targetstorage": targetstorage,
            }
        )
        return self._post_confirmed(api_path("nodes", node, vm_kind(vm_type), vmid, "migrate"), params, confirm)

    # Phase 3: admin/provisioning
    def clone_vm(
        self,
        node: str,
        source_vmid: int,
        newid: int,
        *,
        name: str | None = None,
        full: bool | None = None,
        target: str | None = None,
        storage: str | None = None,
        confirm: bool = False,
    ):
        params = compact_params({"newid": newid, "name": name, "full": bool_param(full), "target": target, "storage": storage})
        return self._post_confirmed(api_path("nodes", node, "qemu", source_vmid, "clone"), params, confirm)

    def create_lxc(
        self,
        node: str,
        vmid: int,
        ostemplate: str,
        storage: str,
        *,
        hostname: str | None = None,
        memory: int | None = None,
        cores: int | None = None,
        net0: str | None = None,
        rootfs: str | None = None,
        password: str | None = None,
        ssh_public_keys: str | None = None,
        confirm: bool = False,
    ):
        params = compact_params(
            {
                "vmid": vmid,
                "ostemplate": ostemplate,
                "storage": storage,
                "hostname": hostname,
                "memory": memory,
                "cores": cores,
                "net0": net0,
                "rootfs": rootfs,
                "password": password,
                "ssh-public-keys": ssh_public_keys,
            }
        )
        return self._post_confirmed(api_path("nodes", node, "lxc"), params, confirm)

    def create_qemu_vm(
        self,
        node: str,
        vmid: int,
        *,
        name: str | None = None,
        memory: int | None = None,
        cores: int | None = None,
        sockets: int | None = None,
        net0: str | None = None,
        scsi0: str | None = None,
        ide2: str | None = None,
        ostype: str | None = None,
        confirm: bool = False,
    ):
        params = compact_params(
            {
                "vmid": vmid,
                "name": name,
                "memory": memory,
                "cores": cores,
                "sockets": sockets,
                "net0": net0,
                "scsi0": scsi0,
                "ide2": ide2,
                "ostype": ostype,
            }
        )
        return self._post_confirmed(api_path("nodes", node, "qemu"), params, confirm)

    def delete_vm(
        self,
        node: str,
        vmid: int,
        vm_type: VmType = "qemu",
        *,
        purge: bool | None = None,
        destroy_unreferenced_disks: bool | None = None,
        confirm: bool = False,
    ):
        params = compact_params({"purge": bool_param(purge), "destroy-unreferenced-disks": bool_param(destroy_unreferenced_disks)})
        return self._delete_confirmed(api_path("nodes", node, vm_kind(vm_type), vmid), params, confirm)

    def resize_disk(self, node: str, vmid: int, disk: str, size: str, *, confirm: bool = False):
        return self._put_confirmed(api_path("nodes", node, "qemu", vmid, "resize"), {"disk": disk, "size": size}, confirm)

    def set_vm_config(self, node: str, vmid: int, config: dict[str, Any], vm_type: VmType = "qemu", *, confirm: bool = False):
        return self._put_confirmed(api_path("nodes", node, vm_kind(vm_type), vmid, "config"), config, confirm)

    def api_request(self, method: str, path: str, params: dict[str, Any] | None = None, *, confirm: bool = False):
        normalized = normalize_api_path(path)
        method_upper = method.upper()
        confirm_mutation(method_upper, normalized, confirm=confirm)
        return self.client.request(method_upper, normalized, params)

    def _post_confirmed(self, path: str, params: dict[str, Any] | None, confirm: bool):
        confirm_mutation("POST", path, confirm=confirm)
        return self.client.post(path, params)

    def _put_confirmed(self, path: str, params: dict[str, Any] | None, confirm: bool):
        confirm_mutation("PUT", path, confirm=confirm)
        return self.client.put(path, params)

    def _delete_confirmed(self, path: str, params: dict[str, Any] | None, confirm: bool):
        confirm_mutation("DELETE", path, confirm=confirm)
        return self.client.delete(path, params)
