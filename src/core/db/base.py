from typing import Any, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import as_declarative, declared_attr

T = TypeVar("T", bound="Base")


@as_declarative()
class Base:
    # Автоматически генерирует имя таблицы в нижнем регистре из имени класса
    @declared_attr
    def __tablename__(cls) -> str:  # noqa: N805
        return cls.__name__.lower()

    def to_dict(self) -> dict[str, Any]:
        """
        Преобразует объект модели в словарь, используя столбцы таблицы.
        """
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def update(self: T, **kwargs) -> T:
        """
        Обновляет атрибуты объекта на основе переданных именованных аргументов.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    async def save(self: T, session: AsyncSession) -> T:
        """
        Асинхронно добавляет объект в сессию и фиксирует изменения в БД.
        """
        session.add(self)
        await session.commit()
        await session.refresh(self)
        return self

    async def delete(self, session: AsyncSession) -> None:
        """
        Асинхронно удаляет объект из сессии и фиксирует изменения в БД.
        """
        await session.delete(self)
        await session.commit()

    @classmethod
    async def get_by_id(cls: type[T], session: AsyncSession, id: Any) -> T:
        """
        Асинхронно возвращает объект по первичному ключу (id).
        """
        return await session.get(cls, id)

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """
        Создает экземпляр модели на основе словаря.
        """
        return cls(**data)
