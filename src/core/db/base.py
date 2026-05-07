from typing import Any, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import as_declarative, declared_attr

T = TypeVar("T", bound="Base")


@as_declarative()
class Base:
    @declared_attr
    def __tablename__(cls) -> str:  # noqa: N805
        return cls.__name__.lower()

    def to_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update(self: T, **kwargs) -> T:
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
        return self

    async def save(self: T, session: AsyncSession, *, refresh: bool = True) -> T:
        """
        добавляет в сессию и делает flush, без commit.
        коммит делает uow/сервис.
        """
        session.add(self)
        await session.flush()
        if refresh:
            await session.refresh(self)
        return self

    async def delete(self, session: AsyncSession) -> None:
        """
        помечает на удаление и делает flush, без commit.
        """
        await session.delete(self)
        await session.flush()

    @classmethod
    async def get_by_id(cls: type[T], session: AsyncSession, id: Any) -> T | None:
        return await session.get(cls, id)

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        return cls(**data)
