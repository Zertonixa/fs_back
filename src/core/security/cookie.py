from fastapi import Response


def set_auth_cookie(response: Response, token: str, max_age_days: int = 7):
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * max_age_days,
        path="/",
    )
