from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import aioboto3
from botocore.config import Config as BotoConfig

from src.core.config.config import settings


def get_session() -> aioboto3.Session:
    return aioboto3.Session()


@asynccontextmanager
async def get_s3_client() -> AsyncIterator:
    session = get_session()
    client_config = BotoConfig(
        region_name=settings.s3.region,
        s3={"addressing_style": settings.s3.addressing_style},
    )

    async with session.client(
        "s3",
        endpoint_url=settings.s3.endpoint,
        aws_access_key_id=settings.s3.access_key,
        aws_secret_access_key=settings.s3.secret_key,
        use_ssl=settings.s3.use_ssl,
        config=client_config,
    ) as client:
        yield client