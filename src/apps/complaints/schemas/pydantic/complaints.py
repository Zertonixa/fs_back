from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.core.enums.complaints import ComplaintStatus


class ComplaintFileRead(BaseModel):
    id: UUID
    complaint_id: UUID
    bucket: str
    object_key: str
    original_filename: str
    content_type: str | None
    size: int
    created_at: datetime
    download_url: str | None = None


class ComplaintRead(BaseModel):
    id: UUID
    user_id: UUID
    text: str
    status: ComplaintStatus
    created_at: datetime
    files: list[ComplaintFileRead] = []


class ComplaintUpdateRequest(BaseModel):
    text: str = Field(..., min_length=1)

class ComplaintStatusUpdateRequest(BaseModel):
    status: ComplaintStatus