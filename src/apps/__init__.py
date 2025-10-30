from fastapi import APIRouter

from .admin import admin_router_v1
from .auth import hint_router_v1
from .booking import hint_router_v1 as booking
from .devices import devices_router_v1
from .notify import notify_router_v1
from .users import user_router_v1

routers: dict[str, APIRouter] = {
    "Auth": hint_router_v1.get_router,
    "Booking": booking.get_router,
    "Devices": devices_router_v1.get_router,
    "Users": user_router_v1.get_router,
    "Admin": admin_router_v1.get_router,
    "Notify": notify_router_v1.get_router,
}

api_router = APIRouter(prefix="/api/v1")

for tag, router in routers.items():
    api_router.include_router(router, tags=[tag])
