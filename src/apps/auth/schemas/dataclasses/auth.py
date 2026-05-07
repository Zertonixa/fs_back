from dataclasses import dataclass


@dataclass
class TgUserPayload:
    telegram_id: int
    username: str | None = None
