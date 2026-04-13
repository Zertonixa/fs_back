import logging
import traceback
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile
from starlette import status as http_status

from src.apps.complaints.di import get_complaints_service
from src.apps.complaints.schemas.dataclasses.complaints import ComplaintCreate
from src.apps.complaints.schemas.pydantic.complaints import (
    ComplaintFileRead,
    ComplaintRead,
    ComplaintStatusUpdateRequest,
)
from src.apps.complaints.services.complaints import ComplaintService
from src.apps.mappers.complaints import dc_file_to_pydantic, dc_to_pydantic
from src.core.dependencies.admin import get_is_admin, require_admin
from src.core.dependencies.user import get_current_user_id
from src.core.enums.complaints import ComplaintStatus

log = logging.getLogger(__name__)

router = APIRouter(prefix="/complaints", tags=["complaints"])


@router.post("", status_code=http_status.HTTP_201_CREATED)
async def create_complaint(
    text: str = Form(...),
    files: list[UploadFile] = File(default=[]),
    service: ComplaintService = Depends(get_complaints_service),
    user_id: UUID = Depends(get_current_user_id),
) -> ComplaintRead:
    try:
        created = await service.create(
            complaint_in=ComplaintCreate(text=text), user_id=user_id, files=files
        )
        return dc_to_pydantic(created)
    except Exception as e:
        log.exception("POST /complaints failed")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", status_code=http_status.HTTP_200_OK)
async def get_my_complaints(
    service: ComplaintService = Depends(get_complaints_service),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: ComplaintStatus | None = Query(None),
    search: str | None = Query(None),
    user_id: UUID = Depends(get_current_user_id),
) -> list[ComplaintRead]:
    complaints = await service.get_complaints(
        limit=limit, offset=offset, status=status, user_id=user_id, search_text=search
    )
    return [dc_to_pydantic(c) for c in complaints]


@router.get("/{complaint_id}", status_code=http_status.HTTP_200_OK)
async def get_complaint(
    complaint_id: UUID,
    service: ComplaintService = Depends(get_complaints_service),
    user_id: UUID = Depends(get_current_user_id),
    is_admin: bool = Depends(get_is_admin),
) -> ComplaintRead:
    complaint = await service.get_by_id(complaint_id, user_id, is_admin)
    return dc_to_pydantic(complaint)


@router.get("/{complaint_id}/files", status_code=http_status.HTTP_200_OK)
async def get_complaint_files(
    complaint_id: UUID,
    service: ComplaintService = Depends(get_complaints_service),
    user_id: UUID = Depends(get_current_user_id),
    is_admin: bool = Depends(get_is_admin),
) -> list[ComplaintFileRead]:
    files_with_urls = await service.get_files_with_urls(complaint_id, user_id, is_admin)
    return [dc_file_to_pydantic(file_dc, download_url=url) for file_dc, url in files_with_urls]


@router.patch("/{complaint_id}", status_code=http_status.HTTP_200_OK)
async def update_complaint(
    complaint_id: UUID,
    text: str = Form(...),
    service: ComplaintService = Depends(get_complaints_service),
    user_id: UUID = Depends(get_current_user_id),
    is_admin: bool = Depends(get_is_admin),
) -> ComplaintRead:
    updated = await service.update(
        complaint_id=complaint_id, text=text, user_id=user_id, is_admin=is_admin
    )
    return dc_to_pydantic(updated)


@router.delete("/{complaint_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_complaint(
    complaint_id: UUID,
    service: ComplaintService = Depends(get_complaints_service),
    user_id: UUID = Depends(get_current_user_id),
    is_admin: bool = Depends(get_is_admin),
) -> Response:
    await service.delete(complaint_id=complaint_id, user_id=user_id, is_admin=is_admin)
    return Response(status_code=http_status.HTTP_204_NO_CONTENT)


@router.get("", response_model=list[ComplaintRead])
async def get_complaints(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: ComplaintStatus | None = Query(None),
    user_id: UUID | None = Query(None),
    search: str | None = Query(None, description="Search by complaint text"),
    service: ComplaintService = Depends(get_complaints_service),
    admin=Depends(require_admin),
) -> list[ComplaintRead]:
    complaints = await service.get_complaints(
        limit=limit, offset=offset, status=status, user_id=user_id, search_text=search
    )
    return [dc_to_pydantic(c) for c in complaints]


@router.patch("/{complaint_id}/status", status_code=http_status.HTTP_200_OK)
async def update_complaint_status(
    complaint_id: UUID,
    payload: ComplaintStatusUpdateRequest,
    service: ComplaintService = Depends(get_complaints_service),
    user_id: UUID = Depends(get_current_user_id),
    is_admin: bool = Depends(get_is_admin),
) -> ComplaintRead:
    updated = await service.update_status(
        complaint_id=complaint_id, new_status=payload.status, user_id=user_id, is_admin=is_admin
    )
    return dc_to_pydantic(updated)
