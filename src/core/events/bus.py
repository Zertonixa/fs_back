from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

TEvent = TypeVar("TEvent")
Handler = Callable[[Any], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._handlers: defaultdict[type[Any], list[Handler]] = defaultdict(list)

    def subscribe(
        self, event_type: type[TEvent], handler: Callable[[TEvent], Awaitable[None]]
    ) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: Any) -> None:
        for h in self._handlers.get(type(event), []):
            await h(event)
