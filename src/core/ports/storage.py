from typing import BinaryIO, Protocol


class FileStoragePort(Protocol):
    async def upload(
        self,
        bucket: str,
        key: str,
        body: bytes | BinaryIO,
        content_type: str | None = None,
    ) -> str: ...
    async def get_url(self, bucket: str, key: str, expires: int = 3600) -> str: ...
    async def delete(self, bucket: str, key: str) -> None: ...
