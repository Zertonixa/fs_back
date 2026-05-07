from fastapi import APIRouter, Depends, Request

from src.apps.weather.di import get_weather_service
from src.apps.weather.services.weather import WeatherService

router = APIRouter(prefix="/weather", tags=["Weather"])


def get_client_ip(request: Request) -> str:
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        x_real_ip = request.headers.get("x-real-ip")
        if x_real_ip:
            ip = x_real_ip.strip()
        else:
            ip = request.client.host if request.client else None

    if not ip:
        raise ValueError("Client IP not found")

    if ip in ("172.18.0.1", "::1", "localhost"):
        return "93.182.46.218"

    return ip


@router.get("/weather")
async def get_weather(
    request: Request, weather_service: WeatherService = Depends(get_weather_service)
) -> dict:
    ip = get_client_ip(request)
    return await weather_service.get_weather_by_ip(ip)
