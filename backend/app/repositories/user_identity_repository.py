import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import UserIdentity


class UserIdentityRepository:
    """Data access for external identities. Never commits."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_issuer_subject(self, issuer: str, subject: str) -> Optional[UserIdentity]:
        # Identity is always looked up by (issuer, subject), never by email.
        stmt = select(UserIdentity).where(
            UserIdentity.issuer == issuer, UserIdentity.subject == subject
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create(
        self,
        user_id: uuid.UUID,
        provider: str,
        issuer: str,
        subject: str,
        tenant_id: Optional[str],
    ) -> UserIdentity:
        identity = UserIdentity(
            user_id=user_id,
            provider=provider,
            issuer=issuer,
            subject=subject,
            tenant_id=tenant_id,
        )
        self.db.add(identity)
        self.db.flush()  # raises IntegrityError here if (issuer, subject) exists
        return identity
