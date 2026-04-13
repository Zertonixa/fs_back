import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class IpAdapter:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
        self.url = "http://ip-api.com/json"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1),
        reraise=True,
    )
    async def fetch_ip(self, ip: str) -> dict:
        response = await self.client.get(
            f"{self.url}/{ip}",
            params={"fields": "status,message,city,lat,lon"},
        )
        response.raise_for_status()
        data = response.json()

        if data["status"] != "success":
            raise ValueError(f"ip-api error: {data.get('message', 'unknown error')}")

        return data

    def normalize(self, data: dict) -> dict:
        return {
            "city": data["city"],
            "lat": data["lat"],
            "lon": data["lon"],
        }