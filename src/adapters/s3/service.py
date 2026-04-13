from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from botocore.exceptions import ClientError

from src.adapters.s3.client import get_s3_client
from src.core.config.config import settings


class S3Service:
    def __init__(self) -> None:
        self.bucket = settings.s3.bucket
        self.bucket_name = self.bucket

    async def ensure_bucket_exists(self) -> None:
        async with get_s3_client() as client:
            try:
                await client.head_bucket(Bucket=self.bucket)
            except ClientError:
                await client.create_bucket(Bucket=self.bucket)

    def build_object_key(self, complaint_id: int, filename: str) -> str:
        ext = Path(filename).suffix
        now = datetime.now(UTC)
        return (
            f"complaints/{now.year}/{now.month:02d}/{now.day:02d}/{complaint_id}/{uuid4().hex}{ext}"
        )

    async def upload_file(self, *, data: bytes, object_key: str, content_type: str | None) -> None:
        async with get_s3_client() as client:
            await client.put_object(
                Bucket=self.bucket,
                Key=object_key,
                Body=data,
                ContentType=content_type or "application/octet-stream",
            )

    async def delete_file(self, object_key: str) -> None:
        async with get_s3_client() as client:
            await client.delete_object(Bucket=self.bucket, Key=object_key)

    async def generate_download_url(self, object_key: str, expires_in: int = 3600) -> str:
        async with get_s3_client() as client:
            url = await client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket, "Key": object_key},
                ExpiresIn=expires_in,
            )

            url = url.replace(settings.s3.endpoint, settings.s3.public_url)
            return url


from abc import ABC, abstractmethod


class IS3Service(ABC):
    @abstractmethod
    async def ensure_bucket_exists(self) -> None: ...

    @abstractmethod
    def build_object_key(self, complaint_id: str, filename: str) -> str: ...

    @abstractmethod
    async def upload_file(
        self, *, data: bytes, object_key: str, content_type: str | None
    ) -> None: ...

    @abstractmethod
    async def delete_file(self, object_key: str) -> None: ...

    @abstractmethod
    async def generate_download_url(self, object_key: str, expires_in: int = 3600) -> str: ...
