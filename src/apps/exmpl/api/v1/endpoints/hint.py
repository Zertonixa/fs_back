"""
Определяйте хэндлеры роутеров FastAPI для версионированных API эндпоинтов.

- Следует разделять роутеры по назначению или же делить все на модули внутри src/apps/
- Избегайте бизнес-логики здесь - следует отдать эту задачу слоям репозиториев и сервисов.
- Используйте Pydantic модели для валидации ответов и запросов.
"""

from fastapi import APIRouter
from starlette import status


class Hint:
    __router: APIRouter = APIRouter(prefix="/hint")

    @property
    def get_router(self):
        return self.__router

    @__router.get(path="/ping", summary="Ping", status_code=status.HTTP_200_OK)
    def ping(self) -> str:
        return "pong"


hint = Hint()
