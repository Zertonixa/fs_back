from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.apps.complaints.repositories.interfaces import IComplaintRepo
from src.apps.complaints.schemas.dataclasses.complaints import Complaint, ComplaintFile
from src.apps.mappers.complaints import orm_file_to_dc, orm_to_dc
from src.core.db.models.complaints import Complaint as ComplaintORM
from src.core.db.models.complaints_files import ComplaintFile as ComplaintFileORM
from src.core.enums.complaints import ComplaintStatus


class ComplaintRepo(IComplaintRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, complaint: Complaint) -> Complaint:
        obj = ComplaintORM(
            user_id=complaint.user_id,
            text=complaint.text,
            status=ComplaintStatus[complaint.status.name],
        )
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)

        return Complaint(
            id=obj.id,
            user_id=obj.user_id,
            text=obj.text,
            status=ComplaintStatus[obj.status.name],
            created_at=obj.created_at,
            files=[],
        )

    async def get_by_id(self, complaint_id: UUID) -> Complaint | None:
        stmt = (
            select(ComplaintORM)
            .options(selectinload(ComplaintORM.files))
            .where(ComplaintORM.id == complaint_id)
        )
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()
        return orm_to_dc(obj) if obj else None

    async def get_by_user(self, user_id: UUID) -> list[Complaint]:
        stmt = (
            select(ComplaintORM)
            .options(selectinload(ComplaintORM.files))
            .where(ComplaintORM.user_id == user_id)
            .order_by(ComplaintORM.created_at.desc())
        )
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        return [orm_to_dc(obj) for obj in rows]

    async def get_all(
        self,
        limit: int = 10,
        offset: int = 0,
        status: ComplaintStatus | None = None,
        user_id: UUID | None = None,
        search_text: str | None = None,
    ) -> list[Complaint]:
        stmt = (
            select(ComplaintORM)
            .options(selectinload(ComplaintORM.files))
            .order_by(ComplaintORM.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        if status:
            stmt = stmt.where(ComplaintORM.status == status)
        if user_id:
            stmt = stmt.where(ComplaintORM.user_id == user_id)
        if search_text:
            stmt = stmt.where(ComplaintORM.text.ilike(f"%{search_text}%"))

        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        return [orm_to_dc(obj) for obj in rows]

    async def save_file(self, complaint_file: ComplaintFile) -> ComplaintFile:
        obj = ComplaintFileORM(
            complaint_id=complaint_file.complaint_id,
            bucket=complaint_file.bucket,
            object_key=complaint_file.object_key,
            original_filename=complaint_file.original_filename,
            content_type=complaint_file.content_type,
            size=complaint_file.size,
        )
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)

        return orm_file_to_dc(obj)

    async def get_files(self, complaint_id: UUID) -> list[ComplaintFile]:
        stmt = (
            select(ComplaintFileORM)
            .where(ComplaintFileORM.complaint_id == complaint_id)
            .order_by(ComplaintFileORM.created_at.asc())
        )
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        return [orm_file_to_dc(obj) for obj in rows]

    async def update_status(self, complaint_id: UUID, status: ComplaintStatus) -> Complaint | None:
        obj = await self.session.get(ComplaintORM, complaint_id)
        if obj is None:
            return None

        obj.status = ComplaintStatus[status.name]
        await self.session.flush()
        await self.session.refresh(obj)

        return Complaint(
            id=obj.id,
            user_id=obj.user_id,
            text=obj.text,
            status=ComplaintStatus[obj.status.name],
            created_at=obj.created_at,
            files=[],
        )

    async def update(
        self, complaint_id: UUID, text: str, status: ComplaintStatus
    ) -> Complaint | None:
        obj = await self.session.get(ComplaintORM, complaint_id)
        if obj is None:
            return None

        obj.text = text
        obj.status = ComplaintStatus[status.name]

        await self.session.flush()
        await self.session.refresh(obj)

        stmt = (
            select(ComplaintORM)
            .options(selectinload(ComplaintORM.files))
            .where(ComplaintORM.id == complaint_id)
        )
        result = await self.session.execute(stmt)
        obj = result.scalar_one()

        return orm_to_dc(obj)

    async def delete_files(self, complaint_id: UUID) -> None:
        stmt = delete(ComplaintFileORM).where(ComplaintFileORM.complaint_id == complaint_id)
        await self.session.execute(stmt)

    async def delete(self, complaint_id: UUID) -> bool:
        obj = await self.session.get(ComplaintORM, complaint_id)
        if obj is None:
            return False

        await self.session.delete(obj)
        await self.session.flush()
        return True
