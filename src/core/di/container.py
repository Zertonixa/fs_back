"""
Если вам привычнее использовать инъекцию зависимостей через app.state...
и fastapi.Request.app.state..., то предлагаю следующую реализацию
контейнера зависимостей
"""
from dataclasses import dataclass
from src.core.ports.storage import FileStoragePort
from src.core.ports.cache import CachePort
from src.core.ports.pubsub import PubSubPort
from src.core.ports.broker import TaskBrokerPort

@dataclass(slots=True)
class Container:
    storage: FileStoragePort
    cache: CachePort
    pubsub: PubSubPort
    broker: TaskBrokerPort

async def build_container(
        storage: FileStoragePort,
        cache: CachePort,
        pubsub: PubSubPort,
        broker: TaskBrokerPort
) -> Container:
    """
    Необходимо прописать логику инициализации сервисов из входящих параметров.
    :param storage:
    :param cache:
    :param pubsub:
    :param broker:
    :return:
    """
    return Container(storage=storage, cache=cache, pubsub=pubsub, broker=broker)

async def shutdown_container(container: Container):
    await container.pubsub.close()
    try:
        client = container.cache._r
        await client.close()
    except Exception:
        pass
