from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.auth.router import router as auth_router
from app.core.config import settings


app = FastAPI(
    title="OIDC Authentication Learning",
    description="Microsoft Entra ID authentication using OIDC",
    version="1.0.0"
)


# Temporary OIDC transaction storage for local learning
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    session_cookie=settings.SESSION_COOKIE_NAME,
    max_age=settings.SESSION_TTL_SECONDS,
    same_site=settings.SESSION_COOKIE_SAMESITE,
    https_only=settings.SESSION_COOKIE_SECURE,
)


# Register authentication routes
app.include_router(auth_router)


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
