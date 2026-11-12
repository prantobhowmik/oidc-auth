from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, verify_origin
from app.auth.session_cookie import clear_session_cookie, read_session_token
from app.core.database import get_db
from app.models import User
from app.services.session_service import SessionService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
def me(response: Response, user: User = Depends(get_current_user)):
    response.headers["Cache-Control"] = "no-store"
    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
    }


@router.post("/logout", status_code=204, dependencies=[Depends(verify_origin)])
def logout(request: Request, db: Session = Depends(get_db)):
    # Local logout only: revokes this app's session. Microsoft's own session stays.
    SessionService(db).revoke(read_session_token(request))
    response = Response(status_code=204)
    clear_session_cookie(response)
    return response
