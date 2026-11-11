"""Declarative base and mixins.

Copied from Pro3AI's pro3ai_generic.base.mixins so the schema conventions stay
compatible for a later merge (UUID primary keys, timezone-aware timestamps).
"""

import uuid
from datetime import datetime

from sqlalchemy import Uuid, func
from sqlalchemy.dialects.oracle import TIMESTAMP as ORACLE_TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    pass


class UUIDMixin:
    @declared_attr
    def id(cls) -> Mapped[uuid.UUID]:
        # Maps to Oracle RAW(16)
        return mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        ORACLE_TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        ORACLE_TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )
