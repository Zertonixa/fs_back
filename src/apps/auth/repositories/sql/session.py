from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.auth.repositories.interfaces import IAuthSessionRepo
from src.core.db.models import AuthSession


class AuthSessionRepo(IAuthSessionRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: UUID,
        jti: UUID,
        expires_at: datetime,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> AuthSession:
        auth_session = AuthSession(
            user_id=user_id,
            jti=jti,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.session.add(auth_session)
        await self.session.flush()
        return auth_session

    async def get_by_jti(self, jti: UUID) -> AuthSession | None:
        stmt = select(AuthSession).where(AuthSession.jti == jti)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def revoke(self, jti: UUID) -> None:
        stmt = (
            update(AuthSession)
            .where(AuthSession.jti == jti, AuthSession.revoked_at.is_(None))
            .values(revoked_at=datetime.now(UTC))
        )
        await self.session.execute(stmt)

    async def revoke_all_by_user(self, user_id: UUID) -> None:
        stmt = (
            update(AuthSession)
            .where(AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None))
            .values(revoked_at=datetime.now(UTC))
        )
        await self.session.execute(stmt)
