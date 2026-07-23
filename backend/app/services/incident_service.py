from datetime import datetime, timezone, timedelta
from typing import Tuple, List, Optional
from sqlalchemy import text

from app.models.incident import Incident, Assignment, RiskAssessment
from app.models.user import User
from app.repositories.incident_repository import IncidentRepository
from app.repositories.user_repository import UserRepository
from app.middleware.error_handler import ValidationError, AuthError, ResourceNotFoundError

# Mapped categories severity scores
SEVERITY_WEIGHTS = {
    "FIRE": 10.0,
    "ASSAULT": 9.0,
    "ACCIDENT": 7.0,
    "THEFT": 5.0,
    "VANDALISM": 4.0,
    "OTHER": 3.0
}

class IncidentService:
    """Orchestrates incident management workflow execution, assignments, and analytical scoring."""

    def __init__(self, incident_repository: IncidentRepository = None, user_repository: UserRepository = None):
        self.incident_repo = incident_repository or IncidentRepository()
        self.user_repo = user_repository or UserRepository()

    def _compute_risk_score(self, category: str, lat: float, lon: float, exclude_id: Optional[str] = None) -> Tuple[float, dict]:
        """Calculates incident risk index (1-100) using category weights, spatial density, and time of day."""
        # 1. Severity weight (S)
        s_weight = SEVERITY_WEIGHTS.get(category, 3.0)

        # 2. Spatial Density within ~1km bounding box in last 30 days (D)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        from app.extensions import db
        query = db.session.query(Incident).filter(
            Incident.is_deleted == False,
            Incident.latitude.between(lat - 0.01, lat + 0.01),
            Incident.longitude.between(lon - 0.01, lon + 0.01),
            Incident.created_at >= thirty_days_ago
        )
        if exclude_id:
            query = query.filter(Incident.id != exclude_id)
        density_count = query.count()
        d_score = float(min(10, density_count))

        # 3. Temporal score based on hour of day (T)
        hour = datetime.now(timezone.utc).hour
        # Night shifts carry higher baseline risks
        t_score = 10.0 if (hour >= 22 or hour < 6) else 4.0

        # Calculate final index using formula
        risk_score = min(100.0, (s_weight * 6.0) + (d_score * 3.5) + (t_score * 0.5))

        factors = {
            "severity_weight": s_weight,
            "spatial_density_count": density_count,
            "temporal_risk_score": t_score
        }
        return round(risk_score, 2), factors

    def create_incident(self, data: dict, reporter_id: str, ip_address: str) -> Incident:
        """Saves a new incident report, triggers background risk scorer analysis, and logs audit events."""
        incident = Incident(
            reporter_id=reporter_id,
            title=data["title"].strip(),
            description=data["description"].strip(),
            category=data["category"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            status="SUBMITTED"
        )
        
        # Save incident record
        saved_incident = self.incident_repo.create(incident)
        self.incident_repo.save()

        # Compute risk parameters immediately
        score, factors = self._compute_risk_score(
            saved_incident.category, 
            float(saved_incident.latitude), 
            float(saved_incident.longitude),
            exclude_id=saved_incident.id
        )
        
        assessment = RiskAssessment(
            incident_id=saved_incident.id,
            risk_score=score,
            factors=factors
        )
        self.incident_repo.create_risk_assessment(assessment)
        self.incident_repo.save()

        # Log status transition log
        from app.services.workflow_service import WorkflowService
        workflow_svc = WorkflowService()
        workflow_svc.log_status_change(
            incident_id=str(saved_incident.id),
            status_from="DRAFT",
            status_to="SUBMITTED",
            changed_by=reporter_id,
            notes="Incident submitted."
        )

        # Log security audit log
        self.user_repo.add_audit_log(
            user_id=reporter_id,
            action="CREATE_INCIDENT",
            ip_address=ip_address,
            payload={"incident_id": str(saved_incident.id), "category": saved_incident.category}
        )

        return saved_incident

    def get_incident(self, incident_id: str) -> Incident:
        """Retrieves active incident record or raises 404 error."""
        incident = self.incident_repo.get_by_id(incident_id)
        if not incident:
            raise ResourceNotFoundError("Incident report could not be found.")
        return incident

    def list_incidents(self, filters: dict, sort_by: str, order: str, page: int, limit: int) -> Tuple[List[Incident], int]:
        """Provides queried paginated list of safety tickets."""
        return self.incident_repo.list_incidents(filters, sort_by, order, page, limit)

    def update_incident(self, incident_id: str, data: dict, user_id: str, user_role: str, ip_address: str) -> Incident:
        """Modifies incident parameters checking security ownership scopes."""
        incident = self.get_incident(incident_id)

        # Enforce write access rules: Only original author, Staff, or Admins
        if user_role not in ["ADMINISTRATOR", "STAFF"] and str(incident.reporter_id) != str(user_id):
            raise AuthError("You do not possess edit permissions for this incident report.")

        # Update properties
        for key in ["title", "description", "category", "latitude", "longitude"]:
            if key in data:
                setattr(incident, key, data[key])
        
        self.incident_repo.save()

        # Log write audits
        self.user_repo.add_audit_log(
            user_id=user_id,
            action="UPDATE_INCIDENT",
            ip_address=ip_address,
            payload={"incident_id": incident_id}
        )
        return incident

    def delete_incident(self, incident_id: str, user_id: str, user_role: str, ip_address: str):
        """Logical soft deletion of incident records."""
        incident = self.get_incident(incident_id)

        # Verify access rules
        if user_role not in ["ADMINISTRATOR", "STAFF"] and str(incident.reporter_id) != str(user_id):
            raise AuthError("You do not possess deletion privileges for this incident report.")

        incident.is_deleted = True
        self.incident_repo.save()

        self.user_repo.add_audit_log(
            user_id=user_id,
            action="DELETE_INCIDENT",
            ip_address=ip_address,
            payload={"incident_id": incident_id}
        )

    def assign_incident(self, data: dict, assigner_id: str, ip_address: str) -> Assignment:
        """Maps an available field officer to target safety incident report."""
        incident_id = str(data["incident_id"])
        officer_id = str(data["officer_id"])

        incident = self.get_incident(incident_id)
        if incident.status in ["RESOLVED", "CLOSED"]:
            raise ValidationError("Cannot route assignments to completed or closed incidents.")

        # Verify target officer role exists
        officer = self.user_repo.get_by_id(officer_id)
        if not officer or officer.role != "OFFICER":
            raise ValidationError("Target assignee must be registered with the OFFICER system role.")

        # Check for pre-existing assignment
        existing = self.incident_repo.get_assignment_by_incident(incident_id)
        if existing:
            if existing.status in ["ASSIGNED", "ACCEPTED"]:
                raise ValidationError("Incident report is already mapped to an active officer.")
            # Remove previous rejected assignment
            from app.extensions import db
            db.session.delete(existing)

        # Create Assignment record
        assignment = Assignment(
            incident_id=incident_id,
            officer_id=officer_id,
            assigned_by=assigner_id,
            status="ASSIGNED"
        )
        
        # Update parent ticket state machine parameters
        incident.status = "ASSIGNED"
        
        saved_assignment = self.incident_repo.create_assignment(assignment)
        self.incident_repo.save()

        # Log status transition log
        from app.services.workflow_service import WorkflowService
        workflow_svc = WorkflowService()
        workflow_svc.log_status_change(
            incident_id=incident_id,
            status_from="SUBMITTED",
            status_to="ASSIGNED",
            changed_by=assigner_id,
            notes=f"Manually assigned to Officer {officer_id}."
        )

        self.user_repo.add_audit_log(
            user_id=assigner_id,
            action="ASSIGN_INCIDENT",
            ip_address=ip_address,
            payload={"incident_id": incident_id, "officer_id": officer_id}
        )
        return saved_assignment

    def update_assignment_status(self, assignment_id: str, data: dict, officer_id: str, ip_address: str) -> Assignment:
        """Handles response operations (accept, reject, resolve) generated by field officers."""
        assignment = self.incident_repo.get_assignment_by_id(assignment_id)
        if not assignment:
            raise ResourceNotFoundError("Assignment record could not be found.")

        # Access check: Only the target officer mapped can execute updates
        if str(assignment.officer_id) != str(officer_id):
            raise AuthError("Access denied: You are not the assigned officer for this incident.")

        status = data["status"]
        incident = self.get_incident(str(assignment.incident_id))
        old_status = incident.status

        if status == "ACCEPTED":
            assignment.status = "ACCEPTED"
            incident.status = "IN_PROGRESS"
        elif status == "REJECTED":
            rejection_reason = data.get("rejection_reason", "").strip()
            if not rejection_reason:
                raise ValidationError("Rejection reason details must be provided.")
            assignment.status = "REJECTED"
            assignment.rejection_reason = rejection_reason
            # Reset incident state to allow re-assignment
            incident.status = "SUBMITTED"
        elif status == "RESOLVED":
            assignment.status = "RESOLVED"
            incident.status = "RESOLVED"
            
        self.incident_repo.save()

        # Log status transition log
        from app.services.workflow_service import WorkflowService
        workflow_svc = WorkflowService()
        workflow_svc.log_status_change(
            incident_id=str(incident.id),
            status_from=old_status,
            status_to=incident.status,
            changed_by=officer_id,
            notes=f"Assignment status updated to {status}."
        )

        # Log write security check
        self.user_repo.add_audit_log(
            user_id=officer_id,
            action=f"ASSIGNMENT_{status}",
            ip_address=ip_address,
            payload={"assignment_id": assignment_id, "incident_id": str(incident.id)}
        )
        return assignment

    def get_dashboard_kpis(self) -> dict:
        """Retrieves incident total stats metrics for dashboard integrations."""
        return self.incident_repo.get_analytics_totals()
