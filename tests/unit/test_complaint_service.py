from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from src.apps.complaints.schemas.dataclasses.complaints import (
    Complaint,
    ComplaintCreate,
    ComplaintFile,
)
from src.apps.complaints.services.complaints import ComplaintService
from src.core.enums.complaints import ComplaintStatus


class FakeComplaintRepo:
    def __init__(self) -> None:
        self.created = None
        self.files = []

    async def create(self, complaint: Complaint) -> Complaint:
        created = Complaint(
            id=uuid.uuid4(),
            user_id=complaint.user_id,
            text=complaint.text,
            status=complaint.status,
            created_at=datetime.now(UTC),
            files=[],
        )
        self.created = created
        return created

    async def save_file(self, complaint_file: ComplaintFile) -> ComplaintFile:
        complaint_file.id = uuid.uuid4()
        complaint_file.created_at = datetime.now(UTC)
        self.files.append(complaint_file)
        return complaint_file

    async def get_by_id(self, complaint_id):
        return Complaint(
            id=complaint_id,
            user_id=self.created.user_id,
            text=self.created.text,
            status=self.created.status,
            created_at=self.created.created_at,
            files=self.files.copy(),
        )


class FakeS3Service:
    def __init__(self, fail_on_upload: bool = False) -> None:
        self.bucket_name = "test-bucket"
        self.fail_on_upload = fail_on_upload
        self.uploaded = []
        self.deleted = []

    def build_object_key(self, complaint_id: str, filename: str) -> str:
        return f"complaints/{complaint_id}/{filename}"

    async def upload_file(self, *, data: bytes, object_key: str, content_type: str | None) -> None:
        if self.fail_on_upload:
            raise RuntimeError("upload failed")
        self.uploaded.append((object_key, data, content_type))

    async def delete_file(self, object_key: str) -> None:
        self.deleted.append(object_key)

    async def generate_download_url(self, object_key: str, expires_in: int = 3600) -> str:
        return f"https://files.test/{object_key}"


class FakeUoW:
    @asynccontextmanager
    async def transaction(self):
        yield self


def make_upload(name: str, body: bytes, content_type: str = "text/plain") -> UploadFile:
    return UploadFile(filename=name, file=BytesIO(body), headers={"content-type": content_type})


@pytest.mark.anyio
async def test_create_uploads_files_and_strips_text() -> None:
    repo = FakeComplaintRepo()
    s3 = FakeS3Service()
    service = ComplaintService(repo, s3, FakeUoW())
    user_id = uuid.uuid4()

    created = await service.create(
        ComplaintCreate(text="  broken machine  "),
        user_id=user_id,
        files=[make_upload("evidence.txt", b"hello")],
    )

    assert created.text == "broken machine"
    assert created.status is ComplaintStatus.SENT
    assert len(repo.files) == 1
    assert repo.files[0].original_filename == "evidence.txt"
    assert s3.uploaded[0][0].endswith("/evidence.txt")


@pytest.mark.anyio
async def test_create_cleans_uploaded_files_when_upload_step_fails() -> None:
    repo = FakeComplaintRepo()
    s3 = FakeS3Service(fail_on_upload=True)
    service = ComplaintService(repo, s3, FakeUoW())

    with pytest.raises(HTTPException, match="Complaint creation failed while uploading files"):
        await service.create(
            ComplaintCreate(text="broken machine"),
            user_id=uuid.uuid4(),
            files=[make_upload("evidence.txt", b"hello")],
        )

    assert s3.deleted == []
