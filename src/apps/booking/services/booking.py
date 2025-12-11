from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from celery.result import AsyncResult
from fastapi import HTTPException, status

from src.adapters.celery.app import celery
from src.adapters.celery.tasks import (
    complete_booking,
    send_booking_end_reminder,
    send_booking_reminder,
)
from src.apps.mappers.booking import create_to_dc
from src.core.db.uow import UoW

from ..repositories.interfaces import IBookingRepo
from ..schemas.dataclasses.booking import Booking, BookingCreate, BookingType


class BookingService:
    def __init__(self, booking_repo: IBookingRepo, uow: UoW):
        self.booking_repo = booking_repo
        self.uow = uow

    async def _get_or_404(self, booking_id: UUID) -> Booking:
        booking = await self.booking_repo.get_by_id(booking_id)
        if booking is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="booking not found")
        return booking

    async def _check_permissions(
        self, booking: Booking, user_id: UUID, is_admin: bool = False
    ) -> None:
        if booking.user_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this booking",
            )

    async def create(
        self, booking_in: BookingCreate, user_id: UUID, telegram_user_id: int | None = None
    ) -> Booking:
        booking_dc = create_to_dc(booking_in, user_id)

        now_utc = datetime.now(UTC)
        starts_at = booking_dc.starts_at
        ends_at = booking_dc.ends_at

        if starts_at >= ends_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start time must be earlier than end time",
            )

        min_duration = timedelta(minutes=30)
        if (ends_at - starts_at) < min_duration:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Minimum booking duration is {min_duration.total_seconds() / 60} minutes",
            )

        buffer = timedelta(minutes=1)
        if starts_at < (now_utc - buffer):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Start time must be in the future"
            )

        if booking_dc.type == "WASHING":
            max_duration = timedelta(hours=8)
            if (ends_at - starts_at) > max_duration:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Maximum booking duration for washing is {max_duration.total_seconds() / 3600} hours",
                )

        elif booking_dc.type == "DRYING":
            max_duration = timedelta(days=2)
            if (ends_at - starts_at) > max_duration:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Maximum booking duration for drying is {max_duration.days} days",
                )

        global_max_duration = timedelta(days=2)
        if (ends_at - starts_at) > global_max_duration:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum booking duration cannot exceed {global_max_duration.days} days",
            )

        max_future_start = timedelta(days=60)
        if starts_at > (now_utc + max_future_start):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot book more than {max_future_start.days} days in advance",
            )

        async with self.uow.transaction():
            if not booking_dc.slot_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="slot_ids must not be empty"
                )

            has_conflict = await self.booking_repo.check_time(
                slot_ids=booking_dc.slot_ids or [],
                booking_type=booking_dc.type,
                starts_at=starts_at,
                ends_at=ends_at,
            )
            if has_conflict:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="slot is already booked for this time range",
                )

            created = await self.booking_repo.create(booking_dc)

            await self._schedule_celery_tasks(created, telegram_user_id, now_utc)

        return created

    async def _schedule_celery_tasks(
        self, booking: Booking, telegram_user_id: int | None, current_time: datetime
    ) -> None:
        try:
            if telegram_user_id:
                start_eta = booking.starts_at - timedelta(minutes=10)
                if start_eta < current_time:
                    start_eta = current_time

                start_task = send_booking_reminder.apply_async(
                    args=[telegram_user_id, str(booking.id), booking.starts_at.isoformat()],
                    eta=start_eta,
                )
                booking.start_reminder_task_id = start_task.id

                end_eta = booking.ends_at - timedelta(minutes=10)
                if end_eta < current_time:
                    end_eta = current_time

                end_task = send_booking_end_reminder.apply_async(
                    args=[telegram_user_id, str(booking.id), booking.ends_at.isoformat()],
                    eta=end_eta,
                )
                booking.end_reminder_task_id = end_task.id

            complete_eta = booking.ends_at
            complete_task = complete_booking.apply_async(args=[str(booking.id)], eta=complete_eta)
            booking.complete_task_id = complete_task.id

            await self.booking_repo.save(booking)

        except Exception:
            if hasattr(booking, "start_reminder_task_id") and booking.start_reminder_task_id:
                AsyncResult(booking.start_reminder_task_id, app=celery).revoke(terminate=False)
            if hasattr(booking, "end_reminder_task_id") and booking.end_reminder_task_id:
                AsyncResult(booking.end_reminder_task_id, app=celery).revoke(terminate=False)
            if hasattr(booking, "complete_task_id") and booking.complete_task_id:
                AsyncResult(booking.complete_task_id, app=celery).revoke(terminate=False)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Booking created but notification scheduling failed",
            )

    async def get_by_id(self, booking_id: UUID) -> Booking | None:
        return await self._get_or_404(booking_id)

    async def find_overlaps(
        self,
        floor: int,
        cso: int,
        booking_type: BookingType,
        starts_at: datetime,
        ends_at: datetime,
    ) -> list[list[dict[str, Any]]]:
        return await self.booking_repo.find_overlaps(
            floor=floor, cso=cso, booking_type=booking_type, starts_at=starts_at, ends_at=ends_at
        )

    async def delete_booking(self, booking_id: UUID, user_id: UUID, is_admin: bool = False) -> None:
        booking = await self._get_or_404(booking_id)
        await self._check_permissions(booking, user_id, is_admin)

        for task_id in (
            booking.start_reminder_task_id,
            booking.end_reminder_task_id,
            booking.complete_task_id,
        ):
            if task_id:
                AsyncResult(task_id, app=celery).revoke(terminate=False)

        async with self.uow.transaction():
            await self.booking_repo.delete(booking_id)

    async def booking_cancel(self, booking_id: UUID, user_id: UUID, is_admin: bool = False):
        booking = await self._get_or_404(booking_id)
        await self._check_permissions(booking, user_id, is_admin)

        for task_id in (
            booking.start_reminder_task_id,
            booking.end_reminder_task_id,
            booking.complete_task_id,
        ):
            if task_id:
                AsyncResult(task_id, app=celery).revoke(terminate=False)
        async with self.uow.transaction():
            return await self.booking_repo.cancel(booking_id)

    async def find_user(self, user_id: UUID):
        return await self.booking_repo.find_user(user_id)

    async def get_my_active(self, user_id: UUID):
        return await self.booking_repo.get_my_active(user_id)

    async def save(self, booking: Booking, user_id: UUID, is_admin: bool = False):
        existing = await self._get_or_404(booking.id)
        await self._check_permissions(existing, user_id, is_admin)

        async with self.uow.transaction():
            await self.booking_repo.save(booking)

    async def get_available_starts(
        self,
        floor: int,
        cso: int,
        booking_type: BookingType,
        from_time: datetime,
        to_time: datetime,
    ) -> list[datetime]:
        return await self.booking_repo.get_available_starts(
            floor=floor, cso=cso, booking_type=booking_type, from_time=from_time, to_time=to_time
        )

    async def get_available_ends(
        self,
        floor: int,
        cso: int,
        booking_type: BookingType,
        start: datetime,
        end_date: datetime | None = None,
    ) -> list[datetime]:
        return await self.booking_repo.get_available_ends(
            floor=floor, cso=cso, booking_type=booking_type, start=start, end_date=end_date
        )
