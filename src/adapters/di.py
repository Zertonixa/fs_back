import httpx

from src.adapters.ip.ip import IpAdapter
from src.adapters.weather.weather import WeatherAdapter


class Container:
    def __init__(self) -> None:
        self.http_client = httpx.AsyncClient(timeout=3.0)
        self.weather_adapter = WeatherAdapter(self.http_client)
        self.ip_adapter = IpAdapter(self.http_client)

    async def close(self) -> None:
        await self.http_client.aclose()
