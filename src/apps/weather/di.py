from src.adapters.di import Container
from src.apps.weather.services.weather import WeatherService


def get_weather_service() -> WeatherService:
    ip_adapter = Container().ip_adapter
    weather_adapter = Container().weather_adapter
    return WeatherService(ip_adapter=ip_adapter, weather_adapter=weather_adapter)
