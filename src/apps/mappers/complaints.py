from src.apps.complaints.schemas.dataclasses.complaints import Complaint as ComplaintDC
from src.apps.complaints.schemas.dataclasses.complaints import ComplaintFile as ComplaintFileDC
from src.apps.complaints.schemas.pydantic.complaints import ComplaintFileRead, ComplaintRead
from src.core.db.models.complaints import Complaint as ComplaintORM
from src.core.db.models.complaints_files import ComplaintFile as ComplaintFileORM


def orm_file_to_dc(obj: ComplaintFileORM) -> ComplaintFileDC:
    return ComplaintFileDC(
        id=obj.id,
        complaint_id=obj.complaint_id,
        bucket=obj.bucket,
        object_key=obj.object_key,
        original_filename=obj.original_filename,
        content_type=obj.content_type,
        size=obj.size,
        created_at=obj.created_at,
    )


def orm_to_dc(obj: ComplaintORM) -> ComplaintDC:
    return ComplaintDC(
        id=obj.id,
        user_id=obj.user_id,
        text=obj.text,
        status=obj.status,
        created_at=obj.created_at,
        files=[orm_file_to_dc(file) for file in getattr(obj, "files", [])],
    )


def dc_file_to_pydantic(dc: ComplaintFileDC, download_url: str | None = None) -> ComplaintFileRead:
    return ComplaintFileRead(
        id=dc.id,
        complaint_id=dc.complaint_id,
        bucket=dc.bucket,
        object_key=dc.object_key,
        original_filename=dc.original_filename,
        content_type=dc.content_type,
        size=dc.size,
        created_at=dc.created_at,
        download_url=(
            download_url if download_url is not None else getattr(dc, "download_url", None)
        ),
    )


def dc_to_pydantic(dc: ComplaintDC) -> ComplaintRead:
    files_pydantic = [dc_file_to_pydantic(f) for f in (dc.files or [])]

    return ComplaintRead(
        id=dc.id,
        user_id=dc.user_id,
        text=dc.text,
        status=dc.status,
        created_at=dc.created_at,
        files=files_pydantic,
    )
