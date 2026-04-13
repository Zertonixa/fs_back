from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, UploadFile, status

from src.adapters.s3.service import IS3Service
from src.apps.complaints.repositories.interfaces import IComplaintRepo
from src.apps.complaints.schemas.dataclasses.complaints import (
    Complaint,
    ComplaintCreate,
    ComplaintFile,
)
from src.core.db.uow import UoW
from src.core.enums.complaints import ComplaintStatus


class ComplaintService:
    def __init__(
        self,
        complaint_repo: IComplaintRepo,
        s3_service: IS3Service,
        uow: UoW,
    ):
        self.complaint_repo = complaint_repo
        self.s3_service = s3_service
        self.uow = uow

    async def _get_or_404(self, complaint_id: UUID) -> Complaint:
        complaint = await self.complaint_repo.get_by_id(complaint_id)
        if complaint is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found",
            )
        return complaint

    async def create(
        self,
        complaint_in: ComplaintCreate,
        user_id: UUID,
        files: Sequence[UploadFile] | None = None,
    ) -> Complaint:
        if not complaint_in.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Complaint text must not be empty",
            )

        files = files or []
        uploaded_keys: list[str] = []

        async with self.uow.transaction():
            created = await self.complaint_repo.create(
                Complaint(
                    user_id=user_id,
                    text=complaint_in.text.strip(),
                    status=ComplaintStatus.SENT,
                )
            )

            try:
                for file in files:
                    content = await file.read()
                    if not content:
                        continue

                    object_key = self.s3_service.build_object_key(
                        complaint_id=str(created.id),
                        filename=file.filename or "file",
                    )

                    await self.s3_service.upload_file(
                        data=content,
                        object_key=object_key,
                        content_type=file.content_type,
                    )
                    uploaded_keys.append(object_key)

                    await self.complaint_repo.save_file(
                        ComplaintFile(
                            complaint_id=created.id,
                            bucket=self.s3_service.bucket_name,
                            object_key=object_key,
                            original_filename=file.filename or "file",
                            content_type=file.content_type,
                            size=len(content),
                        )
                    )

            except Exception:
                for key in uploaded_keys:
                    try:
                        await self.s3_service.delete_file(key)
                    except Exception:
                        pass

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Complaint creation failed while uploading files",
                )

        return await self._get_or_404(created.id)

    async def get_by_id(
        self,
        complaint_id: UUID,
        user_id: UUID,
        is_admin: bool = False,
    ) -> Complaint:
        complaint = await self._get_or_404(complaint_id)

        if complaint.user_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No access",
            )

        for file_dc in complaint.files:
            file_dc.download_url = await self.s3_service.generate_download_url(
                file_dc.object_key
            )

        return complaint

    async def update(
        self,
        complaint_id: UUID,
        text: str,
        user_id: UUID,
        is_admin: bool = False,
    ) -> Complaint:
        complaint = await self._get_or_404(complaint_id)

        if complaint.user_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this complaint",
            )

        if complaint.status == ComplaintStatus.SOLVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solved complaint cannot be updated",
            )

        cleaned_text = text.strip()
        if not cleaned_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Complaint text must not be empty",
            )

        async with self.uow.transaction():
            updated = await self.complaint_repo.update(
                complaint_id=complaint_id,
                text=cleaned_text,
                status=ComplaintStatus.UPDATED,
            )

        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found",
            )

        for file_dc in updated.files:
            file_dc.download_url = await self.s3_service.generate_download_url(
                file_dc.object_key
            )

        return updated

    async def delete(
        self,
        complaint_id: UUID,
        user_id: UUID,
        is_admin: bool = False,
    ) -> None:
        complaint = await self._get_or_404(complaint_id)

        if complaint.user_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this complaint",
            )

        if not is_admin and complaint.status != ComplaintStatus.SENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only complaints in SENT status can be deleted",
            )

        file_keys = [file.object_key for file in complaint.files]

        async with self.uow.transaction():
            await self.complaint_repo.delete_files(complaint_id)
            deleted = await self.complaint_repo.delete(complaint_id)

            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Complaint not found",
                )

        for key in file_keys:
            try:
                await self.s3_service.delete_file(key)
            except Exception:
                pass

    async def get_files_with_urls(
        self,
        complaint_id: UUID,
        user_id: UUID,
        is_admin: bool = False,
    ) -> list[tuple[ComplaintFile, str]]:
        complaint = await self._get_or_404(complaint_id)

        if complaint.user_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No access",
            )

        result: list[tuple[ComplaintFile, str]] = []
        for file_dc in complaint.files:
            url = await self.s3_service.generate_download_url(file_dc.object_key)
            result.append((file_dc, url))

        return result

    async def get_complaints(
        self,
        limit: int = 10,
        offset: int = 0,
        status: ComplaintStatus | None = None,
        user_id: UUID | None = None,
        search_text: str | None = None,
    ) -> list[Complaint]:
        complaints = await self.complaint_repo.get_all(
            limit=limit,
            offset=offset,
            status=status,
            user_id=user_id,
            search_text=search_text,
        )

        for complaint in complaints:
            for file_dc in complaint.files:
                file_dc.download_url = await self.s3_service.generate_download_url(
                    file_dc.object_key
                )

        return complaints
    

    async def update_status(
        self,
        complaint_id: UUID,
        new_status: ComplaintStatus,
        user_id: UUID,
        is_admin: bool = False,
    ) -> Complaint:
        complaint = await self._get_or_404(complaint_id)

        if complaint.user_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to change this complaint",
            )

        async with self.uow.transaction():
            updated = await self.complaint_repo.update_status(complaint_id, new_status)

        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found",
            )

        return await self._get_or_404(updated.id)