import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.extensions import db

class AuditMixin:
    """Provides standard tracking columns for database model updates."""
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)


class User(db.Model, AuditMixin):
    """User representation matching authentication and profile properties."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(30), nullable=False, index=True)  # ADMINISTRATOR, OFFICER, STAFF, CITIZEN, GUEST
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Security tracking properties
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Model relationships
    audit_logs = db.relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"

    @property
    def is_locked(self) -> bool:
        """Returns True if the user account is currently locked out."""
        if self.locked_until:
            now = datetime.now(timezone.utc)
            if self.locked_until > now:
                return True
            # Lock has expired; reset attributes
            self.locked_until = None
            self.failed_login_attempts = 0
            db.session.commit()
        return False


class AuditLog(db.Model):
    """Read-only security log auditing write actions."""
    __tablename__ = "audit_logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)
    payload_details = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    user = db.relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action} by User {self.user_id}>"
