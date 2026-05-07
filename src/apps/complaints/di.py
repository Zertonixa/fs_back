from fastapi import Depends

from src.adapters.s3.service import S3Service
from src.apps.complaints.repositories.sql.complaints import ComplaintRepo
from src.apps.complaints.services.complaints import ComplaintService
from src.core.db.uow import UoW
from src.core.dependencies.db import get_uow


def get_complaints_service(uow: UoW = Depends(get_uow)) -> ComplaintService:
    complaint_repo = ComplaintRepo(uow.session)
    s3_service = S3Service()
    return ComplaintService(complaint_repo=complaint_repo, s3_service=s3_service, uow=uow)
