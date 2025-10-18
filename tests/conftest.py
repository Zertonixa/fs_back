from typing import Any, AsyncGenerator

import pytest
from httpx import AsyncClient


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
async def test_client() -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(base_url="http://test") as client:
        yield client
