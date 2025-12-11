from celery import Celery

from src.core.config.config import settings

celery = Celery(
    "booking",
    broker=settings.redis_pubsub.dsn,
    backend=settings.redis_cache.dsn,
    include=["src.adapters.celery.tasks"],
)

celery.conf.update(
    timezone="Europe/Moscow",
    enable_utc=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)
