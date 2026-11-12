from urllib.parse import urlsplit

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth.session_cookie import read_session_token
from app.core.config import settings
from app.core.database import get_db
from app.models import User
from app.services.session_service import SessionService

UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def _origin_of(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}".lower()


def verify_origin(request: Request) -> None:
    """CSRF defence in depth for cookie-authenticated, state-changing requests.

    SameSite=Lax already blocks cross-site cookies on POST; this additionally
    requires the Origin (or Referer) to be one of our own origins.
    """
    if request.method not in UNSAFE_METHODS:
        return
    allowed = {_origin_of(settings.BACKEND_URL), _origin_of(settings.FRONTEND_URL)}
    source = request.headers.get("origin") or request.headers.get("referer")
    if not source or _origin_of(source) not in allowed:
        raise HTTPException(status_code=403, detail="Origin not allowed")


# Sync dependency: FastAPI runs it in a threadpool, so the sync DB driver
# does not block the event loop.
def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user = SessionService(db).authenticate(read_session_token(request))
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
