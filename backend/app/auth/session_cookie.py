from typing import Optional

from fastapi import Request, Response

from app.core.config import settings


def read_session_token(request: Request) -> Optional[str]:
    return request.cookies.get(settings.SESSION_COOKIE_NAME)


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        max_age=settings.SESSION_ABSOLUTE_TTL_SECONDS,
        path="/",
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE,  # type: ignore[arg-type]
    )


def clear_session_cookie(response: Response) -> None:
    # Attributes must match those used to set it, or the browser keeps the cookie.
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE,  # type: ignore[arg-type]
    )
