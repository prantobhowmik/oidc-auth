import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, Uuid, func
from sqlalchemy.dialects.oracle import TIMESTAMP as ORACLE_TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base, UUIDMixin


class UserIdentity(Base, UUIDMixin):
    """Links a Pro3AI user to an external identity provider account."""

    __tablename__ = "user_identities"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(32), nullable=False)  # MICROSOFT
    issuer: Mapped[str] = mapped_column(String(512), nullable=False)
    subject: Mapped[str] = mapped_column(String(256), nullable=False)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        ORACLE_TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("issuer", "subject", name="uq_user_identities_issuer_subject"),
        Index("ix_user_identities_user_id", "user_id"),
    )
