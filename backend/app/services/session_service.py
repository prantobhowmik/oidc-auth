import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import User
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository

# Avoid a DB write on every request: only bump last_seen_at this often.
TOUCH_INTERVAL = timedelta(seconds=60)


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    # Oracle returns timestamps without tz info; sessions are pinned to UTC
    # (see app/core/database.py), so naive values are UTC.
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


class SessionService:
    """Creates, validates and revokes login sessions. Owns its transactions."""

    def __init__(self, db: Session):
        self.db = db
        self.sessions = SessionRepository(db)
        self.users = UserRepository(db)

    def create(self, user: User) -> str:
        """Create a brand-new session and return the raw cookie token (never stored)."""
        token = secrets.token_urlsafe(32)  # 256 bits
        now = _now()
        expires_at = now + timedelta(seconds=settings.SESSION_ABSOLUTE_TTL_SECONDS)
        try:
            self.sessions.create(_hash(token), user.id, expires_at)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return token

    def authenticate(self, token: Optional[str]) -> Optional[User]:
        """Return the user for a valid session, else None."""
        if not token:
            return None
        row = self.sessions.get_by_hash(_hash(token))
        if row is None or row.revoked_at is not None:
            return None

        now = _now()
        last_seen_at = _as_utc(row.last_seen_at)
        idle_deadline = last_seen_at + timedelta(seconds=settings.SESSION_TTL_SECONDS)
        if now >= _as_utc(row.expires_at) or now >= idle_deadline:
            return None

        user = self.users.get_by_id(row.user_id)
        if user is None or not user.is_active:
            return None

        if now - last_seen_at >= TOUCH_INTERVAL:
            try:
                row.last_seen_at = now
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
        return user

    def revoke(self, token: Optional[str]) -> None:
        """Revoke a session. Idempotent; unknown or already revoked tokens are ignored."""
        if not token:
            return
        row = self.sessions.get_by_hash(_hash(token))
        if row is None or row.revoked_at is not None:
            return
        try:
            row.revoked_at = _now()
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
