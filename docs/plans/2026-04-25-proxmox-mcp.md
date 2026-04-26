# Proxmox MCP Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build and publish a public MCP server that gives Hermes and other agents safe, full-featured access to Proxmox VE.

**Architecture:** Python package with a Proxmox API client, safety/confirmation layer, high-level tool functions, and an MCP server registration module. Use API-token auth first, password-ticket auth as fallback, and a generic guarded `pve_api_request` for endpoint coverage beyond curated tools.

**Tech Stack:** Python 3.11+, `httpx`, official `mcp` Python SDK / FastMCP, `pytest`, `ruff`, GitHub Actions.

---

## Phase 1 — Read-only foundation

### Task 1: Scaffold Python package

**Objective:** Create a Python MCP project with package metadata, README, license, tests, and CI-ready layout.

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `LICENSE`
- Create: `.gitignore`
- Create: `src/proxmox_mcp/__init__.py`
- Create: `tests/`

**Verification:** `uv sync --extra dev` and `uv run pytest` should run.

### Task 2: Implement configuration and safety primitives

**Objective:** Load Proxmox config from environment and gate mutating operations behind explicit confirmation.

**Files:**
- Create: `src/proxmox_mcp/config.py`
- Create: `src/proxmox_mcp/safety.py`
- Test: `tests/test_config.py`
- Test: `tests/test_safety.py`

**Verification:** Tests cover URL normalization, token config, `PVE_VERIFY_SSL`, path validation, and confirmation failures.

### Task 3: Implement Proxmox API client

**Objective:** Provide a small HTTP client for Proxmox `/api2/json` with token auth, optional ticket auth, and structured responses.

**Files:**
- Create: `src/proxmox_mcp/client.py`
- Test: `tests/test_client.py`

**Verification:** Tests use a fake transport to verify auth headers, URL building, params/data handling, and error handling.

### Task 4: Implement read-only tools

**Objective:** Add cluster, node, resource, VM, storage, backup, task, and metric read tools.

**Files:**
- Create: `src/proxmox_mcp/tools.py`
- Test: `tests/test_tools_readonly.py`

**Verification:** Tests assert each tool calls the expected Proxmox path and method.

---

## Phase 2 — Safe state-changing operations

### Task 5: Implement VM/container lifecycle operations

**Objective:** Add start, shutdown, stop, reboot, suspend, and resume with `confirm=true` required.

**Files:**
- Modify: `src/proxmox_mcp/tools.py`
- Test: `tests/test_tools_actions.py`

**Verification:** Tests assert no-confirm raises and confirmed calls hit expected status endpoints.

### Task 6: Implement snapshot and migration operations

**Objective:** Add snapshot create/delete/rollback and VM migration with confirmation gates.

**Files:**
- Modify: `src/proxmox_mcp/tools.py`
- Test: `tests/test_tools_actions.py`

**Verification:** Tests assert endpoints and payloads match Proxmox API expectations.

---

## Phase 3 — Admin/provisioning and full API coverage

### Task 7: Implement provisioning helpers

**Objective:** Add clone, create LXC, create QEMU VM, delete VM, resize disk, and config update tools.

**Files:**
- Modify: `src/proxmox_mcp/tools.py`
- Test: `tests/test_tools_admin.py`

**Verification:** Tests cover confirmation gates and endpoint/payload mapping.

### Task 8: Implement generic API escape hatch

**Objective:** Add `pve_api_request(method, path, params, confirm=false)` for full Proxmox API access with safe defaults.

**Files:**
- Modify: `src/proxmox_mcp/tools.py`
- Test: `tests/test_tools_api_request.py`

**Verification:** GET works without confirmation; mutating methods require confirmation; bad paths are rejected.

### Task 9: Register MCP server tools

**Objective:** Expose all tool functions through FastMCP with stable names and docstrings.

**Files:**
- Create: `src/proxmox_mcp/server.py`
- Test: `tests/test_server.py`

**Verification:** Importing the server succeeds and all expected tool names are registered where the SDK exposes registry inspection.

### Task 10: Add docs, CI, and final verification

**Objective:** Document install/config/safety, add GitHub Actions, run tests/lint, commit, create public GitHub repo, push.

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: `README.md`

**Verification:** `uv run pytest`, `uv run ruff check .`, `git diff --check`, and `gh repo create ... --public --source . --push` complete.
