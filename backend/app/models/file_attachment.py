import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.extensions import db

class FileAttachment(db.Model):
    """Stores metadata of uploaded files, images, and reports."""
    __tablename__ = "file_attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_name = Column(String(255), nullable=False)
    stored_name = Column(String(255), unique=True, nullable=False, index=True)
    extension = Column(String(10), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    checksum = Column(String(32), nullable=False, index=True)  # MD5 checksum to detect duplicate uploads
    storage_path = Column(String(500), nullable=False)
    is_deleted = Column(db.Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    owner = db.relationship("User", foreign_keys=[owner_id])

    def __repr__(self):
        return f"<FileAttachment {self.stored_name} - Size: {self.file_size} bytes>"
