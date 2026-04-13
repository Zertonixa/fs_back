from dataclasses import dataclass, field
from datetime import datetime
from src.core.enums.complaints import ComplaintStatus
from uuid import UUID

@dataclass
class ComplaintFile:
    id: UUID | None = None
    complaint_id: UUID | None = None
    bucket: str = ""
    object_key: str = ""
    original_filename: str = ""
    content_type: str | None = None
    size: int = 0
    created_at: datetime | None = None


@dataclass
class Complaint:
    id: UUID | None = None
    user_id: UUID | None = None
    status: ComplaintStatus = ComplaintStatus.SENT
    text: str = ""
    created_at: datetime | None = None
    files: list[ComplaintFile] = field(default_factory=list)


@dataclass
class ComplaintCreate:
    text: str