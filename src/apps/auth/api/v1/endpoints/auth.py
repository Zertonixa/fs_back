from fastapi import APIRouter, Depends, Request, Response, status

from src.apps.auth.di import get_auth_service
from src.apps.auth.schemas.pydantic.auth import TelegramAuthIn, TokenOut, UserOut
from src.apps.auth.services import AuthService
from src.core.db.models import Users
from src.core.dependencies.admin import is_root_admin_tg
from src.core.dependencies.user import get_current_user
from src.core.security.cookie import clear_auth_cookies, set_access_cookie, set_refresh_cookie
from src.core.security.jwt import get_refresh_payload

router = APIRouter(prefix="/auth")


@router.post(
    "/login", response_model=TokenOut, status_code=status.HTTP_200_OK, summary="Auth with Telegram"
)
async def login(
    payload: TelegramAuthIn,
    request: Request,
    response: Response,
    auth: AuthService = Depends(get_auth_service),
) -> TokenOut:
    access_token, refresh_token, _user = await auth.login_with_telegram(
        payload.init_data,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    set_access_cookie(response, access_token)
    set_refresh_cookie(response, refresh_token)

    return TokenOut(access_token=access_token)


@router.post(
    "/refresh",
    response_model=TokenOut,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
)
async def refresh(
    request: Request,
    response: Response,
    refresh_payload: dict = Depends(get_refresh_payload),
    auth: AuthService = Depends(get_auth_service),
) -> TokenOut:
    access_token, refresh_token = await auth.refresh_tokens(
        refresh_payload,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    set_access_cookie(response, access_token)
    set_refresh_cookie(response, refresh_token)

    return TokenOut(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_200_OK, summary="Logout current session")
async def logout(
    response: Response,
    refresh_payload: dict = Depends(get_refresh_payload),
    auth: AuthService = Depends(get_auth_service),
) -> dict[str, bool]:
    await auth.logout(refresh_payload)
    clear_auth_cookies(response)
    return {"ok": True}


@router.post("/logout-all", status_code=status.HTTP_200_OK, summary="Logout all sessions")
async def logout_all(
    response: Response,
    user: Users = Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
) -> dict[str, bool]:
    await auth.logout_all(user.id)
    clear_auth_cookies(response)
    return {"ok": True}


@router.get("/me", response_model=UserOut)
async def me(user: Users = Depends(get_current_user)) -> UserOut:
    is_root = is_root_admin_tg(user.telegram_id)
    return UserOut(
        id=str(user.id),
        telegram_id=user.telegram_id,
        username=user.username,
        is_root_admin=is_root,
        is_admin=bool(user.is_admin or is_root),
    )
