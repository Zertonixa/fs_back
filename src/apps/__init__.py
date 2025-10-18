from fastapi import APIRouter

from .exmpl import hint_router_v1

routers: dict[str, APIRouter] = {
    "Hint": hint_router_v1.get_router(),
}

api_router = APIRouter(prefix="/api/v1")

for tag, router in routers.items():
    api_router.include_router(router, tags=[tag])
