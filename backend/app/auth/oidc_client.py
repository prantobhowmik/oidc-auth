from authlib.integrations.starlette_client import OAuth

from app.core.config import settings


oauth = OAuth()

oauth.register(
    name="microsoft",

    client_id=settings.MICROSOFT_CLIENT_ID,

    client_secret=settings.MICROSOFT_CLIENT_SECRET,

    server_metadata_url=settings.MICROSOFT_DISCOVERY_URL,

    client_kwargs={
        "scope": "openid profile email",
        "code_challenge_method": "S256",
    },
)
