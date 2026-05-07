from src.adapters.ip.ip import IpAdapter
from src.adapters.weather.weather import WeatherAdapter


class WeatherService:
    def __init__(self, ip_adapter: IpAdapter, weather_adapter: WeatherAdapter) -> None:
        self.ip_adapter = ip_adapter
        self.weather_adapter = weather_adapter

    async def get_weather_by_ip(self, ip: str) -> dict:
        ip_data = await self.ip_adapter.fetch_ip(ip)
        location = self.ip_adapter.normalize(ip_data)

        weather_data = await self.weather_adapter.fetch_weather(
            lat=location["lat"], lon=location["lon"]
        )
        weather = self.weather_adapter.normalize(weather_data)

        return {
            "city": weather["city"] or location["city"],
            "temp": weather["temp"],
            "lat": location["lat"],
            "lon": location["lon"],
        }
