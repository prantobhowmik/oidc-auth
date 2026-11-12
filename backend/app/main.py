from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.auth.router import router as auth_router
from app.auth.session_router import router as session_router
from app.core.config import settings


app = FastAPI(
    title="OIDC Authentication Learning",
    description="Microsoft Entra ID authentication using OIDC",
    version="1.0.0"
)


# OIDC transaction storage only (state, nonce, PKCE verifier) during login.
# SameSite must stay "lax": Microsoft redirects back via a cross-site navigation.
# The authenticated app session is a separate DB-backed cookie (see app/auth/session_cookie.py).
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    session_cookie=settings.OIDC_TRANSACTION_COOKIE_NAME,
    max_age=settings.OIDC_TRANSACTION_TTL_SECONDS,
    same_site="lax",
    https_only=settings.SESSION_COOKIE_SECURE,
)


# Register authentication routes
app.include_router(auth_router)
app.include_router(session_router)


@app.get("/")
async def root():
    return {
        "message": "OIDC Authentication API is running"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }
