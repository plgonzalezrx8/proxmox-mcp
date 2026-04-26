from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_docker_compose_is_primary_http_mcp_entrypoint():
    compose = (ROOT / "docker-compose.yml").read_text()

    assert "proxmox-mcp:" in compose
    assert "build:" in compose
    assert "127.0.0.1:${MCP_PORT:-8000}:${MCP_PORT:-8000}" in compose
    assert "MCP_TRANSPORT:-streamable-http" in compose
    assert "PVE_BASE_URL" in compose
    assert "PVE_VERIFY_SSL" in compose
    assert "PVE_ALLOW_INSECURE_HTTP" in compose
    assert "healthcheck:" in compose


def test_dockerfile_runs_http_mcp_server_by_default():
    dockerfile = (ROOT / "Dockerfile").read_text()

    assert "FROM python:" in dockerfile
    assert "EXPOSE 8000" in dockerfile
    assert "uv sync --frozen --no-dev" in dockerfile
    assert "proxmox-mcp" in dockerfile


def test_env_example_documents_http_and_https_proxmox_modes():
    env_example = (ROOT / ".env.example").read_text()

    assert "PVE_BASE_URL=https://proxmox.lan:8006" in env_example
    assert "PVE_ALLOW_INSECURE_HTTP=false" in env_example
    assert "MCP_TRANSPORT=streamable-http" in env_example
    assert "MCP_PORT=8000" in env_example
    assert "MCP_HOST" not in env_example


def test_readme_makes_docker_compose_the_main_run_path():
    readme = (ROOT / "README.md").read_text()

    docker_section = readme.index("## Run with Docker Compose")
    direct_section = readme.index("## Run without Docker")
    assert docker_section < direct_section
    assert "docker compose up -d --build" in readme
    assert "http://127.0.0.1:8000/mcp" in readme
