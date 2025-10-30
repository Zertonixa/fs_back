from dataclasses import dataclass


@dataclass(frozen=True)
class TgUserPayload:
    telegram_id: str
    username: str | None
