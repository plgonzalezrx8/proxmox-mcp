# proxmox-mcp

A Docker-first Model Context Protocol (MCP) server for Proxmox VE.

It exposes safe, structured tools for read-only cluster inspection, VM/container lifecycle operations, snapshots, migration, provisioning helpers, and a guarded generic Proxmox API escape hatch.

## Status

Alpha. Built with API-token auth and explicit confirmation gates for mutating operations.

## Run with Docker Compose

Docker Compose is the primary supported way to run this MCP server.

```bash
cp .env.example .env
# edit .env with your Proxmox URL and token
docker compose up -d --build
```

By default the MCP server listens on:

```text
http://127.0.0.1:8000/mcp
```

Default MCP transport settings in `.env.example`:

```env
MCP_TRANSPORT=streamable-http
MCP_PORT=8000
MCP_PATH=/mcp
```

Inside Docker, the app binds to `0.0.0.0` in the container, but Compose publishes it only on host loopback by default:

```yaml
ports:
  - "127.0.0.1:8000:8000"
```

Do not publish this unauthenticated MCP endpoint on all interfaces unless you put real network controls in front of it.

Supported MCP transports:

- `streamable-http` — default for Docker and most remote deployments
- `sse` — legacy HTTP/SSE MCP transport
- `stdio` — local subprocess mode

For HTTPS exposure of the MCP endpoint, put this service behind a reverse proxy such as Caddy, Traefik, or nginx and terminate TLS there. Keep the container on plain HTTP internally unless you have a specific reason to do otherwise.

## Proxmox protocol configuration

Prefer HTTPS for the Proxmox API:

```env
PVE_BASE_URL=https://proxmox.lan:8006
PVE_VERIFY_SSL=false # only for self-signed homelab certs
```

If you intentionally need plain HTTP for Proxmox, make it explicit:

```env
PVE_BASE_URL=http://proxmox.lan:8006
PVE_ALLOW_INSECURE_HTTP=true
```

Plain HTTP sends credentials over the network. That is usually a bad idea outside a tightly controlled lab network.

## Authentication

Prefer a Proxmox API token:

```env
PVE_API_TOKEN_ID=user@pam!token-name
PVE_API_TOKEN_SECRET=replace-me
```

Password-ticket auth is also supported, but API tokens are cleaner for MCP:

```env
PVE_USERNAME=user@pam
PVE_PASSWORD=replace-me
```

## Hermes config for Docker HTTP MCP

```yaml
mcp_servers:
  proxmox:
    url: "http://127.0.0.1:8000/mcp"
    timeout: 120
    connect_timeout: 30
```

If deployed on a remote host behind TLS:

```yaml
mcp_servers:
  proxmox:
    url: "https://proxmox-mcp.example.internal/mcp"
    timeout: 120
    connect_timeout: 30
```

## Run without Docker

Local stdio mode remains available for development:

```bash
MCP_TRANSPORT=stdio uvx proxmox-mcp
# or from a checkout:
MCP_TRANSPORT=stdio uv run proxmox-mcp
```

Local HTTP mode without Docker:

```bash
MCP_TRANSPORT=streamable-http MCP_HOST=127.0.0.1 MCP_PORT=8000 MCP_PATH=/mcp uv run proxmox-mcp
```

## Safety model

- `GET` requests are allowed by default.
- `POST`, `PUT`, and `DELETE` require `confirm=true`.
- High-level lifecycle/provisioning tools also require `confirm=true`.
- Secrets are never intentionally returned.
- Generic API paths reject full URLs, query strings, fragments, traversal, encoded traversal, and encoded slash tricks.
- Path segments are validated and encoded before being sent to Proxmox.

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
