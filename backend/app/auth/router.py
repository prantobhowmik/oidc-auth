from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.auth.oidc_client import oauth
from app.core.database import get_db
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


@router.get("/callback", name="microsoft_callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.microsoft.authorize_access_token(request)
    claims = token["userinfo"]

    try:
        # The DB driver is synchronous, so keep it off the event loop.
        user = await run_in_threadpool(UserService(db).login_with_microsoft, claims)
    except InactiveUserError:
        raise HTTPException(status_code=403, detail="User is deactivated")
    except InvalidIdentityError:
        raise HTTPException(status_code=400, detail="Invalid identity token")

    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
    }
