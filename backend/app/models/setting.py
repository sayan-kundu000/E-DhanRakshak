import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db

class SystemSetting(db.Model):
    """Represents application-level system variables and feature flags."""
    __tablename__ = "system_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(db.Text, nullable=False)  # JSON string or plain text value
    description = Column(db.Text, nullable=True)
    category = Column(String(50), default="SYSTEM", nullable=False)  # SYSTEM, SECURITY, NOTIFICATION

    def __repr__(self):
        return f"<SystemSetting {self.key}: {self.value[:30]}>"


class UserPreference(db.Model):
    """Represents user-specific UI and notification alert routing preferences."""
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    preferences_json = Column(JSONB, nullable=False)  # stores notification preference flags, dark_mode etc.

    # Relationship
    user = db.relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<UserPreference for User {self.user_id}>"
