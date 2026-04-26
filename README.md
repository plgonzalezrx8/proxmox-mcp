# proxmox-mcp

A Model Context Protocol (MCP) server for Proxmox VE.

It exposes safe, structured tools for read-only cluster inspection, VM/container lifecycle operations, snapshots, migration, provisioning helpers, and a guarded generic Proxmox API escape hatch.

## Status

Alpha. Built with API-token auth and explicit confirmation gates for mutating operations.

## Configuration

Prefer a Proxmox API token:

```bash
export PVE_BASE_URL="https://proxmox.lan:8006"
export PVE_API_TOKEN_ID="user@pam!token-name"
export PVE_API_TOKEN_SECRET="secret-value"
export PVE_VERIFY_SSL="false" # only for self-signed homelab certs
```

Password-ticket auth is also supported, but API tokens are cleaner for MCP:

```bash
export PVE_USERNAME="user@pam"
export PVE_PASSWORD="password"
```

## Run

```bash
uvx proxmox-mcp
# or from a checkout:
uv run proxmox-mcp
```

## Hermes config

```yaml
mcp_servers:
  proxmox:
    command: "uvx"
    args: ["proxmox-mcp"]
    env:
      PVE_BASE_URL: "https://proxmox.lan:8006"
      PVE_API_TOKEN_ID: "user@pam!token-name"
      PVE_API_TOKEN_SECRET: "..."
      PVE_VERIFY_SSL: "false"
    timeout: 120
    connect_timeout: 30
```

## Safety model

- `GET` requests are allowed by default.
- `POST`, `PUT`, and `DELETE` require `confirm=true`.
- High-level lifecycle/provisioning tools also require `confirm=true`.
- Secrets are never intentionally returned.
- Generic API paths reject full URLs and traversal attempts.

## Tool coverage

### Phase 1: Read-only

- `pve_get_version`
- `pve_get_cluster_status`
- `pve_list_nodes`
- `pve_list_resources`
- `pve_list_vms`
- `pve_get_vm_status`
- `pve_get_vm_config`
- `pve_list_storage`
- `pve_list_backups`
- `pve_get_task_status`
- `pve_get_node_metrics`

### Phase 2: Safe actions

- `pve_start_vm`
- `pve_shutdown_vm`
- `pve_stop_vm`
- `pve_reboot_vm`
- `pve_suspend_vm`
- `pve_resume_vm`
- `pve_create_snapshot`
- `pve_delete_snapshot`
- `pve_rollback_snapshot`
- `pve_migrate_vm`

### Phase 3: Admin/provisioning + escape hatch

- `pve_clone_vm`
- `pve_create_lxc`
- `pve_create_qemu_vm`
- `pve_delete_vm`
- `pve_resize_disk`
- `pve_set_vm_config`
- `pve_api_request`

## Development

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
```
