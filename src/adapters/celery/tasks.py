import asyncio
import logging
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from aiogram import Bot
from celery import shared_task

from src.core.config.config import settings
from src.core.db.db import SessionLocal
from src.core.db.models.booking import Booking as BookingORM
from src.core.db.models.booking import BookingStatus, BookingType

BOT_TOKEN = settings.bot.bot_token
logger = logging.getLogger("booking_tasks")

LOCAL_TZ = ZoneInfo("Europe/Moscow")


def _format_dt_local(dt_str: str) -> str:

    dt = datetime.fromisoformat(dt_str)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    else:
        dt = dt.astimezone(UTC)

    dt_local = dt.astimezone(LOCAL_TZ)
    return dt_local.strftime("%d.%m.%Y %H:%M")


def _send_telegram_message(telegram_id: int, text: str) -> None:
    async def _inner() -> None:
        async with Bot(BOT_TOKEN) as bot:
            await bot.send_message(telegram_id, text, parse_mode="HTML")

    asyncio.run(_inner())


@shared_task(name="booking.send_reminder")
def send_booking_reminder(telegram_id: int, booking_id: str, starts_at: str) -> None:
    logger.info(
        "[TASK START] booking.send_reminder | telegram_id=%s | booking_id=%s | starts_at=%s",
        telegram_id,
        booking_id,
        starts_at,
    )

    with SessionLocal() as session:
        try:
            booking: BookingORM | None = session.get(BookingORM, booking_id)

            if booking is None:
                logger.warning("[SKIP] booking %s not found", booking_id)
                return

            if booking.status != BookingStatus.NEW:
                logger.warning(
                    "[SKIP] booking %s has status=%s, not NEW",
                    booking_id,
                    booking.status,
                )
                return

            pretty_start = _format_dt_local(starts_at)

            text = (
                "<b>⏰ Напоминание о бронировании</b>\n"
                f"<b>ID:</b> <code>{booking_id}</code>\n"
                f"<b>Начало:</b> {pretty_start}"
            )

            logger.info(
                "[SEND] sending message to telegram_id=%s, text='%s'",
                telegram_id,
                text,
            )

            _send_telegram_message(telegram_id, text)

            logger.info("[OK] reminder sent to %s", telegram_id)

        except Exception as e:
            logger.exception(
                "[ERROR] reminder for booking %s: %s",
                booking_id,
                e,
            )


@shared_task(name="booking.complete")
def complete_booking(booking_id: str) -> None:
    logger.info("[TASK START] booking.complete | booking_id=%s", booking_id)

    with SessionLocal() as session:
        try:
            booking: BookingORM | None = session.get(BookingORM, booking_id)

            if booking is None:
                logger.warning("[SKIP] booking %s not found", booking_id)
                return

            if booking.status != BookingStatus.NEW:
                logger.warning(
                    "[SKIP] booking %s has status=%s, skip complete",
                    booking_id,
                    booking.status,
                )
                return

            booking.status = BookingStatus.DONE
            booking.updated_at = datetime.now(UTC)

            session.add(booking)
            session.commit()

            logger.info("[OK] booking %s marked as DONE", booking_id)

        except Exception as e:
            session.rollback()
            logger.exception("[ERROR] complete booking %s: %s", booking_id, e)


@shared_task(name="booking.send_end_reminder")
def send_booking_end_reminder(
    telegram_id: int,
    booking_id: str,
    ends_at: str,
) -> None:
    logger.info(
        "[TASK START] booking.send_end_reminder | telegram_id=%s | booking_id=%s | ends_at=%s",
        telegram_id,
        booking_id,
        ends_at,
    )

    with SessionLocal() as session:
        try:
            booking: BookingORM | None = session.get(BookingORM, booking_id)

            if booking is None:
                logger.warning("[SKIP] booking %s not found", booking_id)
                return

            if booking.status != BookingStatus.NEW:
                logger.warning(
                    "[SKIP] booking %s has status=%s, skip end reminder",
                    booking_id,
                    booking.status,
                )
                return

            if booking.type == BookingType.WASHING:
                place_label = "стиральную машинку"
            else:
                place_label = "сушильную комнату"

            pretty_end = _format_dt_local(ends_at)

            text = (
                "<b>⏰ Скоро закончится бронирование</b>\n"
                f"<b>ID:</b> <code>{booking_id}</code>\n"
                f"<b>Окончание:</b> {pretty_end}\n"
                f"Пожалуйста, освободите {place_label} через 10 минут."
            )

            logger.info(
                "[SEND] sending end-reminder to telegram_id=%s, text='%s'",
                telegram_id,
                text,
            )

            _send_telegram_message(telegram_id, text)

            logger.info("[OK] end reminder sent to %s", telegram_id)

        except Exception as e:
            logger.exception(
                "[ERROR] end reminder for booking %s: %s",
                booking_id,
                e,
            )
