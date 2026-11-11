from typing import Any, Mapping, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User
from app.repositories.user_identity_repository import UserIdentityRepository
from app.repositories.user_repository import UserRepository

MICROSOFT = "MICROSOFT"


class InactiveUserError(Exception):
    """The matched user exists but is deactivated."""


class InvalidIdentityError(Exception):
    """The ID token claims are missing issuer or subject."""


class UserService:
    """Find-or-create logic after a successful OIDC login.

    Owns the transaction: commits on success, rolls back on failure.
    """

    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.identities = UserIdentityRepository(db)

    def login_with_microsoft(self, claims: Mapping[str, Any]) -> User:
        issuer: Optional[str] = claims.get("iss")
        subject: Optional[str] = claims.get("sub")
        if not issuer or not subject:
            raise InvalidIdentityError("ID token is missing 'iss' or 'sub'")

        email = claims.get("email") or claims.get("preferred_username")
        display_name = claims.get("name")
        tenant_id = claims.get("tid")

        try:
            user = self._find_or_create(issuer, subject, tenant_id, email, display_name)
            if not user.is_active:
                raise InactiveUserError(str(user.id))
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        self.db.refresh(user)
        return user

    def _find_or_create(
        self,
        issuer: str,
        subject: str,
        tenant_id: Optional[str],
        email: Optional[str],
        display_name: Optional[str],
    ) -> User:
        identity = self.identities.get_by_issuer_subject(issuer, subject)

        if identity is None:
            try:
                # SAVEPOINT: a duplicate only undoes this block, not the whole session.
                with self.db.begin_nested():
                    user = self.users.create(email=email, display_name=display_name)
                    self.identities.create(user.id, MICROSOFT, issuer, subject, tenant_id)
                return user
            except IntegrityError:
                # Two logins for a new identity raced; the other one won. Use theirs.
                identity = self.identities.get_by_issuer_subject(issuer, subject)
                if identity is None:
                    raise

        user = self.users.get_by_id(identity.user_id)
        if user is None:  # cannot happen with the FK, but fail loudly
            raise RuntimeError("Identity points to a missing user")

        # Refresh profile on subsequent logins; never overwrite with an empty value.
        if email and user.email != email:
            user.email = email
        if display_name and user.display_name != display_name:
            user.display_name = display_name
        if tenant_id and identity.tenant_id != tenant_id:
            identity.tenant_id = tenant_id
        return user
