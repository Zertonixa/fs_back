from fastapi import APIRouter, Depends, status

from src.core.dependencies import get_auth_service
from src.core.security import get_user_id_from_payload

from ....schemas.pydantic.auth import TelegramAuthIn, TokenOut, UserOut
from ....services import AuthService


class Auth:
    __router: APIRouter = APIRouter(prefix="/auth")

    @property
    def get_router(self):
        return self.__router

    @__router.post(path="/login", summary="Auth", status_code=status.HTTP_200_OK)
    async def login(payload: TelegramAuthIn, auth: AuthService = Depends(get_auth_service)):
        return TokenOut(access_token=auth.login_with_telegram(payload.init_data))

    @__router.get(path="/me", summary="Auth", status_code=status.HTTP_200_OK)
    async def me(user=Depends(get_user_id_from_payload)):
        return UserOut(user)


auth = Auth()
