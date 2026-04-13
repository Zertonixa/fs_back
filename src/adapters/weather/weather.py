import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config.config import settings


class WeatherAdapter:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
        self.url = "https://api.weatherapi.com/v1/current.json"
        self.api_key = settings.weather.weather_api_key

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1), reraise=True)
    async def fetch_weather(self, lat: float, lon: float) -> dict:
        response = await self.client.get(
            self.url, params={"key": self.api_key, "q": f"{lat},{lon}", "lang": "ru"}
        )
        response.raise_for_status()
        return response.json()

    def normalize(self, data: dict) -> dict:
        return {"temp": data["current"]["temp_c"], "city": data["location"]["name"]}
