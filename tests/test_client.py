from __future__ import annotations

import json

import httpx
import pytest

from proxmox_mcp.client import ProxmoxApiError, ProxmoxClient
from proxmox_mcp.config import ProxmoxConfig


def make_client(handler):
    cfg = ProxmoxConfig(
        base_url="https://proxmox.lan:8006",
        api_token_id="root@pam!mcp",
        api_token_secret="secret",
        verify_ssl=False,
    )
    return ProxmoxClient(cfg, transport=httpx.MockTransport(handler))


def test_client_sends_token_auth_and_wraps_data():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers.get("authorization")
        return httpx.Response(200, json={"data": {"version": "8.2"}})

    client = make_client(handler)

    result = client.get("/version")

    assert seen["url"] == "https://proxmox.lan:8006/api2/json/version"
    assert seen["auth"] == "PVEAPIToken=root@pam!mcp=secret"
    assert result == {"data": {"version": "8.2"}}


def test_client_uses_query_params_for_get_and_form_for_post():
    bodies = []

    def handler(request: httpx.Request) -> httpx.Response:
        bodies.append((str(request.url), request.content.decode()))
        return httpx.Response(200, json={"data": "UPID:test"})

    client = make_client(handler)

    client.get("/cluster/resources", {"type": "vm"})
    client.post("/nodes/pve/qemu/100/status/start", {"skiplock": 1})

    assert bodies[0] == ("https://proxmox.lan:8006/api2/json/cluster/resources?type=vm", "")
    assert bodies[1] == (
        "https://proxmox.lan:8006/api2/json/nodes/pve/qemu/100/status/start",
        "skiplock=1",
    )


def test_client_raises_on_proxmox_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"errors": {"vmid": "missing"}, "message": "bad"})

    client = make_client(handler)

    with pytest.raises(ProxmoxApiError) as exc:
        client.get("/nodes")

    assert exc.value.status_code == 500
    assert "vmid" in json.dumps(exc.value.payload)
