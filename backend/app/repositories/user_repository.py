from typing import Optional, List
from app.extensions import db
from app.models.user import User, AuditLog

class UserRepository:
    """Encapsulates data access queries for User and AuditLog tables."""

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Queries user database record by UUID primary key (ignoring soft deleted users)."""
        return db.session.query(User).filter(
            User.id == user_id, 
            User.is_deleted == False
        ).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Queries active, non-deleted user record matching target email address."""
        if not email:
            return None
        return db.session.query(User).filter(
            User.email == email.strip().lower(),
            User.is_deleted == False
        ).first()

    def create(self, user: User) -> User:
        """Adds a newly instantiated User record to the transaction session."""
        db.session.add(user)
        db.session.flush()  # Populates user.id UUID prior to commits
        return user

    def save(self, user: User) -> User:
        """Commits transaction modifications to persist user changes."""
        db.session.commit()
        return user

    def add_audit_log(self, user_id: Optional[str], action: str, ip_address: str, payload: Optional[dict] = None) -> AuditLog:
        """Saves a security log documenting write operations."""
        log = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            payload_details=payload
        )
        db.session.add(log)
        db.session.commit()
        return log
