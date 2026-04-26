from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest


@dataclass
class FakeClient:
    calls: list[tuple[str, str, dict[str, Any] | None]] = field(default_factory=list)
    response: dict[str, Any] = field(default_factory=lambda: {"data": "ok"})

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.calls.append(("GET", path, params))
        return self.response

    def post(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.calls.append(("POST", path, params))
        return self.response

    def put(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.calls.append(("PUT", path, params))
        return self.response

    def delete(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.calls.append(("DELETE", path, params))
        return self.response

    def request(self, method: str, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.calls.append((method.upper(), path, params))
        return self.response


@pytest.fixture
def fake_client() -> FakeClient:
    return FakeClient()
