from fastapi import APIRouter

from .admin import admin_router_v1
from .auth import auth_router_v1
from .booking import booking_router_v1
from .slots import slots_router_v1
from .users import user_router_v1

routers: dict[str, APIRouter] = {
    "Auth": auth_router_v1,
    "Booking": booking_router_v1,
    "Devices": slots_router_v1,
    "Users": user_router_v1,
    "Admin": admin_router_v1,
}

api_router = APIRouter(prefix="/api/v1")

for tag, router in routers.items():
    api_router.include_router(router, tags=[tag])
