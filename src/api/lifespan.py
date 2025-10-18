"""
Управление жизненным циклом приложения

- Определяйте здесь то, что должно происходить до и после запуска приложения.
- Инициализируйте ресурсы (Подключения к БД, Redis, S3, и тд.).
- Правильно и чисто закрывайте подключения.

Используйте `lifespan` аргумент объекта fastapi.FastAPI для конфигурации жизненного цикла приложения
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.logger import configure_logger, get_logger

# from src.core.db import init_db_connection
# from src.repository.s3.s3 import init_s3_client
# from src.core.redis import init_redis, close_redis  # если будешь юзать Redis


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Инициализация логгирования
    configure_logger()
    logger = get_logger()
    logger.info("App startup: initializing resources")

    # Например: init_db_connection()
    # Например: await init_redis()
    # Например: await init_s3_client()

    yield  # <- здесь приложение начинает работать

    logger.info("App shutdown: releasing resources")

    # Например: await close_redis()
