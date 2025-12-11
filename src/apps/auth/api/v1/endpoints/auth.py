
from fastapi import APIRouter, Depends, Response, status

from src.core.db.models import Users
from src.core.dependencies.user import get_current_user
from src.core.security.cookie import set_auth_cookie

from ....di import get_auth_service
from ....schemas.pydantic.auth import TelegramAuthIn, TokenOut, UserOut
from ....services import AuthService

router = APIRouter(prefix="/auth")


@router.post(
    "/login",
    response_model=TokenOut,
    status_code=status.HTTP_200_OK,
    summary="Auth with Telegram",
)
async def login(
    payload: TelegramAuthIn,
    response: Response,
    auth: AuthService = Depends(get_auth_service),
) -> TokenOut:
    access_token, user = await auth.login_with_telegram(payload.initData)
    set_auth_cookie(response, access_token)
    return TokenOut(access_token=access_token)


@router.get("/me", response_model=UserOut)
async def me(
    user: Users = Depends(get_current_user),
) -> UserOut:
    return UserOut(
        id=str(user.id),
        telegram_id=user.telegram_id,
        username=user.username,
    )
