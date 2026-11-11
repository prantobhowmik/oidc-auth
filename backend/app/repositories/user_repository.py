import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
    """Data access for users. Never commits; the service owns the transaction."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return self.db.get(User, user_id)

    def create(self, email: Optional[str], display_name: Optional[str]) -> User:
        user = User(email=email, display_name=display_name)
        self.db.add(user)
        self.db.flush()  # assigns the id without committing
        return user
