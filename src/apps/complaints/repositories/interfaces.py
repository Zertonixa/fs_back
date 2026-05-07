from abc import ABC, abstractmethod
from uuid import UUID

from src.apps.complaints.schemas.dataclasses.complaints import Complaint, ComplaintFile
from src.core.enums.complaints import ComplaintStatus


class IComplaintRepo(ABC):
    @abstractmethod
    async def create(self, complaint: Complaint) -> Complaint: ...

    @abstractmethod
    async def get_by_id(self, complaint_id: UUID) -> Complaint | None: ...

    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> list[Complaint]: ...

    @abstractmethod
    async def save_file(self, complaint_file: ComplaintFile) -> ComplaintFile: ...

    @abstractmethod
    async def get_files(self, complaint_id: UUID) -> list[ComplaintFile]: ...

    @abstractmethod
    async def update_status(
        self, complaint_id: UUID, status: ComplaintStatus
    ) -> Complaint | None: ...

    @abstractmethod
    async def update(
        self, complaint_id: UUID, text: str, status: ComplaintStatus
    ) -> Complaint | None: ...

    @abstractmethod
    async def delete(self, complaint_id: UUID) -> bool: ...

    @abstractmethod
    async def delete_files(self, complaint_id: UUID) -> None: ...

    @abstractmethod
    async def get_all(
        self,
        limit: int = 10,
        offset: int = 0,
        status: ComplaintStatus | None = None,
        user_id: UUID | None = None,
        search_text: str | None = None,
    ) -> list[Complaint]: ...
