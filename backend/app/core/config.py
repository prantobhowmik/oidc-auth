from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MICROSOFT_CLIENT_ID: str
    MICROSOFT_CLIENT_SECRET: str
    MICROSOFT_TENANT_ID: str

    MICROSOFT_DISCOVERY_URL: str

    BACKEND_URL: str = "http://localhost:5050"
    FRONTEND_URL: str = "http://localhost:5555"

    SESSION_SECRET_KEY: str

    SESSION_COOKIE_NAME: str = "oidc_transaction"
    SESSION_COOKIE_SECURE: bool = False
    SESSION_COOKIE_SAMESITE: str = "lax"

    SESSION_TTL_SECONDS: int = 600

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
