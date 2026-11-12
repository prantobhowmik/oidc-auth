from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MICROSOFT_CLIENT_ID: str
    MICROSOFT_CLIENT_SECRET: str
    MICROSOFT_TENANT_ID: str

    MICROSOFT_DISCOVERY_URL: str

    BACKEND_URL: str = "http://localhost:5050"
    FRONTEND_URL: str = "http://localhost:5555"

    SESSION_SECRET_KEY: str

    # Short-lived cookie that only carries OIDC state/nonce/PKCE during login.
    OIDC_TRANSACTION_COOKIE_NAME: str = "oidc_transaction"
    OIDC_TRANSACTION_TTL_SECONDS: int = 600

    # Application session cookie (opaque id; the session itself lives in the DB).
    SESSION_COOKIE_NAME: str = "app_session"
    SESSION_COOKIE_SECURE: bool = False
    SESSION_COOKIE_SAMESITE: str = "lax"
    SESSION_TTL_SECONDS: int = 1800  # idle timeout
    SESSION_ABSOLUTE_TTL_SECONDS: int = 43200  # hard limit, 12 hours

    DB_HOST: str = "localhost"
    DB_PORT: int = 1522
    DB_SERVICE_NAME: str = "FREEPDB1"
    DB_USER: str
    DB_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
