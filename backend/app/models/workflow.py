import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.extensions import db

class IncidentHistory(db.Model):
    """Audits incident state transition log changes."""
    __tablename__ = "incident_histories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    status_from = Column(String(30), nullable=False)
    status_to = Column(String(30), nullable=False)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    notes = Column(db.Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    incident = db.relationship("Incident", foreign_keys=[incident_id])
    user = db.relationship("User", foreign_keys=[changed_by])

    def __repr__(self):
        return f"<IncidentHistory {self.incident_id}: {self.status_from} -> {self.status_to}>"
