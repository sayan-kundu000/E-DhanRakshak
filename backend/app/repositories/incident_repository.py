from typing import Optional, List, Tuple
from app.extensions import db
from app.models.incident import Incident, Assignment, RiskAssessment

class IncidentRepository:
    """Encapsulates transactional operations and query selections for operational incidents."""

    def get_by_id(self, incident_id: str) -> Optional[Incident]:
        """Queries incident by primary key, skipping soft-deleted rows."""
        return db.session.query(Incident).filter(
            Incident.id == incident_id,
            Incident.is_deleted == False
        ).first()

    def list_incidents(
        self, 
        filters: dict, 
        sort_by: str = "created_at", 
        order: str = "desc", 
        page: int = 1, 
        limit: int = 10
    ) -> Tuple[List[Incident], int]:
        """Queries multiple incidents matching criteria, supporting pagination and sorting."""
        query = db.session.query(Incident).filter(Incident.is_deleted == False)

        # Apply search filters
        if "status" in filters:
            query = query.filter(Incident.status == filters["status"])
        if "category" in filters:
            query = query.filter(Incident.category == filters["category"])
        if "reporter_id" in filters:
            query = query.filter(Incident.reporter_id == filters["reporter_id"])

        # Calculate counts prior to offsets slicing
        total_records = query.count()

        # Apply sorting order
        sort_column = getattr(Incident, sort_by, Incident.created_at)
        if order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Slicing page offsets
        offset = (page - 1) * limit
        records = query.offset(offset).limit(limit).all()

        return records, total_records

    def create(self, incident: Incident) -> Incident:
        """Adds a newly logged Incident to transaction session."""
        db.session.add(incident)
        db.session.flush()
        return incident

    def save(self):
        """Commits current session transactions."""
        db.session.commit()

    def create_assignment(self, assignment: Assignment) -> Assignment:
        """Adds field assignment mapping resource row."""
        db.session.add(assignment)
        db.session.flush()
        return assignment

    def get_assignment_by_id(self, assignment_id: str) -> Optional[Assignment]:
        """Locates specific assignment record."""
        return db.session.query(Assignment).filter(Assignment.id == assignment_id).first()

    def get_assignment_by_incident(self, incident_id: str) -> Optional[Assignment]:
        """Locates assignment matching incident ID."""
        return db.session.query(Assignment).filter(Assignment.incident_id == incident_id).first()

    def list_officer_assignments(self, officer_id: str) -> List[Assignment]:
        """Queries all assignment entries designated for target officer."""
        return db.session.query(Assignment).filter(
            Assignment.officer_id == officer_id
        ).order_by(Assignment.created_at.desc()).all()

    def create_risk_assessment(self, assessment: RiskAssessment) -> RiskAssessment:
        """Persists risk predictions scores."""
        db.session.add(assessment)
        db.session.flush()
        return assessment

    def get_risk_by_incident(self, incident_id: str) -> Optional[RiskAssessment]:
        """Locates risk assessment linking target incident."""
        return db.session.query(RiskAssessment).filter(RiskAssessment.incident_id == incident_id).first()

    def get_analytics_totals(self) -> dict:
        """Collects dashboard KPI aggregates (active incidents, resolved rates, categories count)."""
        total = db.session.query(Incident).filter(Incident.is_deleted == False).count()
        resolved = db.session.query(Incident).filter(
            Incident.is_deleted == False, 
            Incident.status == "RESOLVED"
        ).count()
        open_cases = db.session.query(Incident).filter(
            Incident.is_deleted == False,
            Incident.status.in_(["SUBMITTED", "ASSIGNED", "IN_PROGRESS"])
        ).count()

        return {
            "total_incidents": total,
            "resolved_incidents": resolved,
            "open_incidents": open_cases,
            "resolution_rate": round((resolved / total * 100), 2) if total > 0 else 0.0
        }
