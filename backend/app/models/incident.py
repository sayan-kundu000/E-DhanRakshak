import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.extensions import db
from app.models.user import AuditMixin

class Incident(db.Model, AuditMixin):
    """Database model mapping citizen or staff public safety incident reports."""
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(String, nullable=False)
    category = Column(String(50), nullable=False, index=True)  # THEFT, ASSAULT, FIRE, ACCIDENT, VANDALISM, OTHER
    status = Column(String(30), default="SUBMITTED", nullable=False, index=True)  # DRAFT, SUBMITTED, ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    attachment_url = Column(String(500), nullable=True)

    # Relationships
    reporter = db.relationship("User", foreign_keys=[reporter_id])
    assignment = db.relationship("Assignment", back_populates="incident", uselist=False, cascade="all, delete-orphan")
    risk_assessment = db.relationship("RiskAssessment", back_populates="incident", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Incident {self.title[:20]} ({self.status})>"


class Assignment(db.Model):
    """Junction mapping assigned field personnel to incidents."""
    __tablename__ = "assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, unique=True)
    officer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    status = Column(String(30), default="ASSIGNED", nullable=False)  # ASSIGNED, ACCEPTED, REJECTED, RESOLVED
    rejection_reason = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    incident = db.relationship("Incident", back_populates="assignment")
    officer = db.relationship("User", foreign_keys=[officer_id])
    assigner = db.relationship("User", foreign_keys=[assigned_by])

    def __repr__(self):
        return f"<Assignment Incident {self.incident_id} to Officer {self.officer_id}>"


class RiskAssessment(db.Model):
    """Stores analytical risk index scores and computational factors calculations."""
    __tablename__ = "risk_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, unique=True)
    risk_score = Column(Numeric(5, 2), nullable=False)
    factors = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    incident = db.relationship("Incident", back_populates="risk_assessment")

    def __repr__(self):
        return f"<RiskAssessment Incident {self.incident_id} - Score: {self.risk_score}>"
