from authlib.integrations.base_client import OAuthError
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth.oidc_client import oauth
from app.auth.session_cookie import read_session_token, set_session_cookie
from app.core.database import get_db
from app.services.session_service import SessionService
from app.services.user_service import (
    InactiveUserError,
    InvalidIdentityError,
    UserService,
)

router = APIRouter(prefix="/auth/microsoft", tags=["auth"])


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("microsoft_callback")
    return await oauth.microsoft.authorize_redirect(request, redirect_uri)


def _complete_login(db: Session, claims, old_token):
    """Find/create the user and issue a fresh session (sync DB work)."""
    user = UserService(db).login_with_microsoft(claims)
    sessions = SessionService(db)
    # Never reuse a pre-login session: drop any old one, issue a new id.
    sessions.revoke(old_token)
    return user, sessions.create(user)


@router.get("/callback", name="microsoft_callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.microsoft.authorize_access_token(request)
    except OAuthError:
        # Bad/expired state, user cancelled at Microsoft, invalid token, ...
        raise HTTPException(status_code=400, detail="Login failed. Please try again.")

    claims = token.get("userinfo")
    if not claims:
        raise HTTPException(status_code=400, detail="Login failed. Please try again.")

    # TEMP DEBUG (remove before commit): show what Microsoft really returns.
    import json
    print("=== ID TOKEN CLAIMS ===")
    print(json.dumps(dict(claims), indent=2, default=str))
    print("=== TOKEN RESPONSE KEYS (values hidden) ===")
    print(sorted(token.keys()), "| scope:", token.get("scope"))

    try:
        # The DB driver is synchronous, so keep it off the event loop.
        user, session_token = await run_in_threadpool(
            _complete_login, db, claims, read_session_token(request)
        )
    except InactiveUserError:
        raise HTTPException(status_code=403, detail="User is deactivated")
    except InvalidIdentityError:
        raise HTTPException(status_code=400, detail="Invalid identity token")

    # No frontend yet: return the user JSON. Later this becomes a redirect.
    response = JSONResponse(
        {
            "id": str(user.id),
            "email": user.email,
            "display_name": user.display_name,
        },
        headers={"Cache-Control": "no-store"},
    )
    set_session_cookie(response, session_token)
    return response
