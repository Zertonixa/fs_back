from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.apps.weather.api.v1.endpoints.weather import get_client_ip


@pytest.mark.anyio
async def test_get_client_ip_prefers_x_forwarded_for() -> None:
    request = SimpleNamespace(
        headers={"x-forwarded-for": "203.0.113.10, 10.0.0.1", "x-real-ip": "198.51.100.1"},
        client=SimpleNamespace(host="127.0.0.1"),
    )

    assert get_client_ip(request) == "203.0.113.10"


@pytest.mark.anyio
async def test_get_client_ip_maps_localhost_to_demo_ip() -> None:
    request = SimpleNamespace(headers={}, client=SimpleNamespace(host="localhost"))

    assert get_client_ip(request) == "93.182.46.218"
