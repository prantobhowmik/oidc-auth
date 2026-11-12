"""Model registry: importing this registers all models on Base.metadata."""

from app.models.user import User
from app.models.user_identity import UserIdentity
from app.models.user_session import UserSession

__all__ = ["User", "UserIdentity", "UserSession"]
