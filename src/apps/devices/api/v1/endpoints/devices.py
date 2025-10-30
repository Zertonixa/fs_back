from fastapi import APIRouter, Query
from starlette import status as http_status

from ....schemas.pydantic.devices import Device


class Devices:
    __router: APIRouter = APIRouter(prefix="/devices", tags=["Devices"])

    @property
    def get_router(self) -> APIRouter:
        return self.__router

    @staticmethod
    def _get_current_user_id() -> int:
        return 123

    @__router.get(path="/", status_code=http_status.HTTP_200_OK)
    async def get_all_devices(
        type: str | None = Query(
            None, alias="type", description="Тип устройства (washing, drying)"
        ),
    ) -> list[Device]:
        return "ok"

    @__router.post(path="/", status_code=http_status.HTTP_201_CREATED)
    async def create_device(device: Device) -> Device:
        return {"status": "ok"}

    @__router.delete(path="/{device_id}", status_code=http_status.HTTP_204_NO_CONTENT)
    async def delete_device(device_id: int) -> None:
        return None

    @__router.patch(path="/edit/{device_id}")
    async def edit_device(device: Device) -> Device:
        return "ok"


devices = Devices()
