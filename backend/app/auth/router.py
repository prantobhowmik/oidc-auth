from fastapi import APIRouter, Request

from app.auth.oidc_client import oauth

router = APIRouter(prefix="/auth/microsoft", tags=["auth"])


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("microsoft_callback")
    return await oauth.microsoft.authorize_redirect(request, redirect_uri)


@router.get("/callback", name="microsoft_callback")
async def callback(request: Request):
    token = await oauth.microsoft.authorize_access_token(request)
    user = token["userinfo"]

    return {
        "name": user.get("name"),
        "email": user.get("email") or user.get("preferred_username"),
        "sub": user.get("sub"),
        "tenant_id": user.get("tid"),
    }
