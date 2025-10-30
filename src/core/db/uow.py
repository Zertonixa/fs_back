from sqlalchemy.ext.asyncio import AsyncSession

from .db import async_session_maker


class UnitOfWork:
    def __init__(self):
        self.session: AsyncSession | None = None

    async def __aenter__(self):
        self.session = async_session_maker()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()

    def get_repo(self, repo_cls):
        return repo_cls(self.session)
