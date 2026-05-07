from __future__ import annotations

import pytest

from src.apps.weather.di import get_weather_service

pytestmark = pytest.mark.integration


class StubWeatherService:
    async def get_weather_by_ip(self, ip: str) -> dict:
        return {"city": "Vilnius", "temp": 18, "lat": 54.6872, "lon": 25.2797}


class FailingWeatherService:
    async def get_weather_by_ip(self, ip: str) -> dict:
        raise RuntimeError("weather upstream unavailable")


@pytest.mark.anyio
async def test_weather_route_returns_success_payload(app, client) -> None:
    app.dependency_overrides[get_weather_service] = lambda: StubWeatherService()

    response = await client.get("/api/v1/weather/weather", headers={"x-real-ip": "203.0.113.10"})

    assert response.status_code == 200
    body = response.json()
    assert body["city"] == "Vilnius"
    assert body["temp"] == 18


@pytest.mark.anyio
async def test_weather_route_returns_500_on_upstream_failure(app, client) -> None:
    app.dependency_overrides[get_weather_service] = lambda: FailingWeatherService()

    response = await client.get("/api/v1/weather/weather", headers={"x-real-ip": "203.0.113.10"})

    assert response.status_code == 500
