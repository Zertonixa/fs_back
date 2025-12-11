from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


class UoW:
    def __init__(self, session: AsyncSession):
        self.session = session

    @asynccontextmanager
    async def transaction(self):
        try:
            yield self
            await self.session.commit()
        except:
            await self.session.rollback()
            raise
