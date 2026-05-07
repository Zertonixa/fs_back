from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import types
import urllib.parse
import uuid
from collections.abc import AsyncGenerator
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if "celery" not in sys.modules:
    celery_module = types.ModuleType("celery")

    class Celery:
        def __init__(self, *args, **kwargs):
            self.conf = SimpleNamespace(update=lambda *a, **k: None)

    def shared_task(*args, **kwargs):
        def decorator(fn):
            return fn

        return decorator

    celery_module.Celery = Celery
    celery_module.shared_task = shared_task
    sys.modules["celery"] = celery_module

if "celery.result" not in sys.modules:
    celery_result_module = types.ModuleType("celery.result")

    class AsyncResult:
        def __init__(self, task_id, app=None):
            self.task_id = task_id
            self.app = app

        def revoke(self, terminate: bool = False):
            return None

    celery_result_module.AsyncResult = AsyncResult
    sys.modules["celery.result"] = celery_result_module

if "src.adapters.celery.app" not in sys.modules:
    celery_app_module = types.ModuleType("src.adapters.celery.app")
    celery_app_module.celery = SimpleNamespace()
    sys.modules["src.adapters.celery.app"] = celery_app_module

if "src.adapters.celery.tasks" not in sys.modules:
    celery_tasks_module = types.ModuleType("src.adapters.celery.tasks")

    class _Task:
        def __init__(self, prefix: str):
            self.prefix = prefix
            self.calls = 0

        def apply_async(self, *args: Any, **kwargs: Any) -> SimpleNamespace:
            self.calls += 1
            return SimpleNamespace(id=f"{self.prefix}-{self.calls}")

    celery_tasks_module.send_booking_reminder = _Task("start")
    celery_tasks_module.send_booking_end_reminder = _Task("end")
    celery_tasks_module.complete_booking = _Task("done")
    sys.modules["src.adapters.celery.tasks"] = celery_tasks_module

if "tenacity" not in sys.modules:
    tenacity_module = types.ModuleType("tenacity")

    def retry(*args, **kwargs):
        def decorator(fn):
            return fn

        return decorator

    def stop_after_attempt(*args, **kwargs):
        return None

    def wait_exponential(*args, **kwargs):
        return None

    tenacity_module.retry = retry
    tenacity_module.stop_after_attempt = stop_after_attempt
    tenacity_module.wait_exponential = wait_exponential
    sys.modules["tenacity"] = tenacity_module


from src.api.main import app as fastapi_app  # noqa: E402
from src.apps.complaints.di import get_complaints_service  # noqa: E402
from src.apps.complaints.repositories.sql.complaints import ComplaintRepo  # noqa: E402
from src.apps.complaints.services.complaints import ComplaintService  # noqa: E402
from src.core.config.config import settings  # noqa: E402
from src.core.db.base import Base  # noqa: E402
from src.core.db.models import (  # noqa: E402,F401
    AdminHistory,
    AuthSession,
    Booking,
    BookingSlots,
    Complaint,
    ComplaintFile,
    Notify,
    Slot,
    Users,
)
from src.core.db.uow import UoW  # noqa: E402
from src.core.dependencies.db import get_async_session, get_uow  # noqa: E402
from src.core.events.bus import EventBus  # noqa: E402
from src.core.security.jwt import (  # noqa: E402
    create_access_token,
    create_refresh_token,
    decode_token,
)

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5433/fs_back_test"
)


class FakeS3Service:
    def __init__(self) -> None:
        self.bucket_name = "complaints-test"
        self.files: dict[str, bytes] = {}

    async def ensure_bucket_exists(self) -> None:
        return None

    def build_object_key(self, complaint_id: str, filename: str) -> str:
        return f"complaints/{complaint_id}/{filename}"

    async def upload_file(self, *, data: bytes, object_key: str, content_type: str | None) -> None:
        self.files[object_key] = data

    async def delete_file(self, object_key: str) -> None:
        self.files.pop(object_key, None)

    async def generate_download_url(self, object_key: str, expires_in: int = 3600) -> str:
        return f"https://files.test/{object_key}"


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.fixture(scope="session")
def session_factory(engine):
    return async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False, autocommit=False
    )


@pytest.fixture(scope="session")
def event_bus() -> EventBus:
    return EventBus()


@pytest.fixture()
async def db_cleanup(engine) -> AsyncGenerator[None, None]:
    yield
    table_names = [table.name for table in reversed(Base.metadata.sorted_tables)]
    if table_names:
        joined = ", ".join(table_names)
        async with engine.begin() as conn:
            await conn.execute(text(f"TRUNCATE TABLE {joined} RESTART IDENTITY CASCADE"))


@pytest.fixture()
async def db_session(session_factory, db_cleanup) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


@pytest.fixture()
def fake_s3() -> FakeS3Service:
    return FakeS3Service()


@pytest.fixture()
def app(session_factory, event_bus: EventBus, fake_s3: FakeS3Service):
    async def override_get_async_session():
        async with session_factory() as session:
            yield session

    async def override_get_uow():
        async with session_factory() as session:
            yield UoW(session=session, event_bus=event_bus)

    async def override_get_complaints_service():
        async with session_factory() as session:
            yield ComplaintService(
                complaint_repo=ComplaintRepo(session),
                s3_service=fake_s3,
                uow=UoW(session=session, event_bus=event_bus),
            )

    original_overrides = dict(fastapi_app.dependency_overrides)
    fastapi_app.dependency_overrides[get_async_session] = override_get_async_session
    fastapi_app.dependency_overrides[get_uow] = override_get_uow
    fastapi_app.dependency_overrides[get_complaints_service] = override_get_complaints_service
    fastapi_app.state.event_bus = event_bus

    try:
        yield fastapi_app
    finally:
        fastapi_app.dependency_overrides = original_overrides


@pytest.fixture()
async def client(app) -> AsyncGenerator[AsyncClient, Any]:
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


# ---------- helper factory ----------
@pytest.fixture()
def db_helpers(session_factory):
    async def create_user(
        *, telegram_id: int, username: str | None, is_admin: bool = False, is_banned: bool = False
    ) -> Users:
        async with session_factory() as session:
            user = Users(
                telegram_id=telegram_id, username=username, is_admin=is_admin, is_banned=is_banned
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def create_slot(
        *, type_: str, floor: int, cso: int, row: int, place: int, status: bool = True
    ) -> Slot:
        from src.core.db.models.slot import Type as SlotType

        async with session_factory() as session:
            slot = Slot(
                type=SlotType[type_], floor=floor, cso=cso, row=row, place=place, status=status
            )
            session.add(slot)
            await session.commit()
            await session.refresh(slot)
            return slot

    async def create_booking_row(
        *, user_id, slot_ids: list[uuid.UUID], type_: str, starts_at, ends_at, status: str = "NEW"
    ) -> Booking:
        from src.core.db.models.booking import BookingStatus, BookingType

        async with session_factory() as session:
            booking = Booking(
                user_id=user_id,
                type=BookingType[type_],
                status=BookingStatus[status],
                starts_at=starts_at,
                ends_at=ends_at,
                start_reminder_task_id=None,
                end_reminder_task_id=None,
                complete_task_id=None,
            )
            session.add(booking)
            await session.flush()

            for slot_id in slot_ids:
                session.add(BookingSlots(booking_id=booking.id, slot_id=slot_id))

            await session.commit()
            await session.refresh(booking)
            return booking

    async def create_complaint_row(*, user_id, text_value: str, status_value) -> Complaint:
        async with session_factory() as session:
            complaint = Complaint(user_id=user_id, text=text_value, status=status_value)
            session.add(complaint)
            await session.commit()
            await session.refresh(complaint)
            return complaint

    async def create_complaint_file_row(
        *,
        complaint_id,
        object_key: str,
        filename: str,
        content_type: str = "image/png",
        size: int = 10,
    ) -> ComplaintFile:
        async with session_factory() as session:
            file_row = ComplaintFile(
                complaint_id=complaint_id,
                bucket="complaints-test",
                object_key=object_key,
                original_filename=filename,
                content_type=content_type,
                size=size,
            )
            session.add(file_row)
            await session.commit()
            await session.refresh(file_row)
            return file_row

    async def create_admin_history_row(
        *, moderator_id, target_user_id, action, description: str
    ) -> AdminHistory:
        async with session_factory() as session:
            row = AdminHistory(
                moderator_id=moderator_id,
                target_user_id=target_user_id,
                action=action,
                description=description,
            )
            session.add(row)
            await session.commit()
            await session.refresh(row)
            return row

    async def auth_as(client: AsyncClient, user: Users) -> tuple[str, str]:
        async with session_factory() as session:
            access_token = create_access_token(
                subject=str(user.id), extra_claims={"tg": user.telegram_id}
            )
            refresh_token, expires_at = create_refresh_token(
                subject=str(user.id), extra_claims={"tg": user.telegram_id}
            )
            refresh_payload = decode_token(refresh_token)
            auth_session = AuthSession(
                user_id=user.id,
                jti=uuid.UUID(refresh_payload["jti"]),
                expires_at=expires_at,
                revoked_at=None,
                user_agent="pytest",
                ip_address="127.0.0.1",
            )
            session.add(auth_session)
            await session.commit()

        client.cookies.set("access_token", access_token)
        client.cookies.set("refresh_token", refresh_token)
        return access_token, refresh_token

    return SimpleNamespace(
        create_user=create_user,
        create_slot=create_slot,
        create_booking_row=create_booking_row,
        create_complaint_row=create_complaint_row,
        create_complaint_file_row=create_complaint_file_row,
        create_admin_history_row=create_admin_history_row,
        auth_as=auth_as,
    )


def build_init_data(bot_token: str, telegram_id: int, username: str | None) -> str:
    user_payload = {"id": telegram_id}
    if username is not None:
        user_payload["username"] = username

    data = {
        "auth_date": "1710000000",
        "query_id": "AAEAAAE",
        "user": json.dumps(user_payload, separators=(",", ":")),
    }
    pairs = [f"{k}={v}" for k, v in sorted(data.items())]
    data_check_string = "\n".join(pairs)

    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    signature = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    data["hash"] = signature
    return urllib.parse.urlencode(data)


@pytest.fixture()
def telegram_init_data():
    def _factory(telegram_id: int, username: str | None = None) -> str:
        return build_init_data(settings.bot.bot_token, telegram_id, username)

    return _factory


def pytest_collection_modifyitems(config, items):
    for item in items:
        path = str(item.fspath)
        if "/tests/unit/" in path or "\\tests\\unit\\" in path:
            item.add_marker(pytest.mark.unit)
        elif "/tests/integration/" in path or "\\tests\\integration\\" in path:
            item.add_marker(pytest.mark.integration)
        elif "/tests/e2e/" in path or "\\tests\\e2e\\" in path:
            item.add_marker(pytest.mark.e2e)
