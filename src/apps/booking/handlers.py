from src.apps.booking.repositories.sql.booking import BookingRepo
from src.core.events.types import SlotUpdatedEvent


class CancelBookingsOnSlotUpdated:
    def __init__(self, repo: BookingRepo):
        self.repo = repo

    async def handle(self, event: SlotUpdatedEvent) -> None:
        await self.repo.cancel_all_by_slot(event.slot_id)
