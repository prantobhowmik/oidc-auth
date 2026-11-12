import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Index, String, Uuid, func
from sqlalchemy.dialects.oracle import TIMESTAMP as ORACLE_TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base, UUIDMixin


class UserSession(Base, UUIDMixin):
    """A server-side login session. The cookie holds a random token; only its hash is stored."""

    __tablename__ = "user_sessions"

    # SHA-256 hex of the cookie value, so a DB leak does not yield usable sessions.
    session_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        ORACLE_TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        ORACLE_TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )
    # Absolute expiry; the idle timeout is enforced against last_seen_at.
    expires_at: Mapped[datetime] = mapped_column(ORACLE_TIMESTAMP(timezone=True), nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        ORACLE_TIMESTAMP(timezone=True), nullable=True
    )

    __table_args__ = (Index("ix_user_sessions_user_id", "user_id"),)
