import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.extensions import db

class Notification(db.Model):
    """Represents in-app notifications and alerts dispatched to users."""
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    message = Column(db.Text, nullable=False)
    type = Column(String(30), default="IN_APP", nullable=False)  # IN_APP, EMAIL, SMS
    priority = Column(String(20), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationship
    user = db.relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<Notification {self.id} for User {self.user_id} - Read: {self.is_read}>"
