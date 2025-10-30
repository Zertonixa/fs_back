from collections.abc import Awaitable, Callable
from typing import Protocol

MessageHandler = Callable[[str, bytes], Awaitable[None]]


class PubSubPort(Protocol):
    async def publish(self, channel: str, data: bytes) -> None: ...
    async def subscribe(self, channel: str, handler: MessageHandler) -> None: ...
    async def close(self) -> None: ...
