from typing import Optional

from sqlalchemy import Boolean, String, true
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """A person inside Pro3AI."""

    __tablename__ = "users"

    # Not unique: the Microsoft email claim can be missing or unverified.
    # Identity is established by user_identities (issuer, subject), not by email.
    email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )
