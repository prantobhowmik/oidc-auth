from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import UserSession


class SessionRepository:
    """Data access for sessions. Never commits; the service owns the transaction."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, session_hash: str, user_id, expires_at: datetime) -> UserSession:
        row = UserSession(session_hash=session_hash, user_id=user_id, expires_at=expires_at)
        self.db.add(row)
        self.db.flush()
        return row

    def get_by_hash(self, session_hash: str) -> Optional[UserSession]:
        stmt = select(UserSession).where(UserSession.session_hash == session_hash)
        return self.db.execute(stmt).scalar_one_or_none()
