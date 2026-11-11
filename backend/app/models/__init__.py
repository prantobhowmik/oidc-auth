"""Model registry: importing this registers all models on Base.metadata."""

from app.models.user import User
from app.models.user_identity import UserIdentity

__all__ = ["User", "UserIdentity"]
