import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from app.extensions import db
from app.models.incident import Incident, Assignment
from app.models.user import User
from app.models.workflow import IncidentHistory
from app.repositories.workflow_repository import WorkflowRepository
from app.repositories.incident_repository import IncidentRepository
from app.repositories.user_repository import UserRepository
from app.services.notification_service import NotificationService
from app.middleware.error_handler import ValidationError, ResourceNotFoundError

logger = logging.getLogger("app.workflow")

class WorkflowService:
    """Orchestrates incident status transition histories, spatial auto-assignment matching, and alerts escalation checks."""

    def __init__(
        self,
        workflow_repository: WorkflowRepository = None,
        incident_repository: IncidentRepository = None,
        user_repository: UserRepository = None,
        notification_service: NotificationService = None
    ):
        self.workflow_repo = workflow_repository or WorkflowRepository()
        self.incident_repo = incident_repository or IncidentRepository()
        self.user_repo = user_repository or UserRepository()
        self.notification_service = notification_service or NotificationService()

    def log_status_change(self, incident_id: str, status_from: str, status_to: str, changed_by: str, notes: Optional[str] = None) -> IncidentHistory:
        history = IncidentHistory(
            incident_id=incident_id,
            status_from=status_from,
            status_to=status_to,
            changed_by=changed_by,
            notes=notes
        )
        saved = self.workflow_repo.create_history_log(history)
        self.workflow_repo.save()
        
        logger.info(f"STATUS CHANGE: Incident {incident_id} transition from {status_from} to {status_to} by User {changed_by}")
        return saved

    def get_history(self, incident_id: str) -> List[IncidentHistory]:
        return self.workflow_repo.get_incident_history(incident_id)

    def auto_assign_incident(self, incident_id: str, assigner_id: str, ip_address: str) -> Assignment:
        """Finds the least busy available officer and dispatches the incident assignment."""
        incident = self.incident_repo.get_by_id(incident_id)
        if not incident:
            raise ResourceNotFoundError("Incident not found.")
        if incident.status in ["RESOLVED", "CLOSED"]:
            raise ValidationError("Cannot auto-assign completed or closed incidents.")

        # 1. Fetch all active officers
        officers = db.session.query(User).filter(
            User.role == "OFFICER",
            User.is_active == True,
            User.is_deleted == False
        ).all()

        if not officers:
            raise ValidationError("No active officers available in the system for routing.")

        # 2. Score each officer based on workload and spatial distance
        best_officer = None
        min_workload = float("inf")
        min_distance = float("inf")

        for officer in officers:
            # Active workload count: assignments assigned or accepted
            workload = db.session.query(Assignment).filter(
                Assignment.officer_id == officer.id,
                Assignment.status.in_(["ASSIGNED", "ACCEPTED"])
            ).count()

            # Spatial distance (Euclidean distance approximation)
            # Find the officer's last reported location from their assignments, or default to incident location
            last_assignment = db.session.query(Assignment).join(
                Incident, Incident.id == Assignment.incident_id
            ).filter(
                Assignment.officer_id == officer.id
            ).order_by(Assignment.created_at.desc()).first()

            if last_assignment and last_assignment.incident:
                distance = (float(incident.latitude) - float(last_assignment.incident.latitude))**2 + \
                           (float(incident.longitude) - float(last_assignment.incident.longitude))**2
            else:
                distance = 0.0  # Default to 0 if no historical assignments

            # Select the officer with the lowest workload. Break ties with distance.
            if workload < min_workload:
                min_workload = workload
                min_distance = distance
                best_officer = officer
            elif workload == min_workload and distance < min_distance:
                min_distance = distance
                best_officer = officer

        if not best_officer:
            raise ValidationError("Could not allocate assignment to any officer.")

        # 3. Trigger standard assignment creation logic
        # Check and remove previous rejected assignment if exists
        existing = self.incident_repo.get_assignment_by_incident(incident_id)
        if existing:
            if existing.status in ["ASSIGNED", "ACCEPTED"]:
                raise ValidationError("Incident is already mapped to an active officer.")
            db.session.delete(existing)

        assignment = Assignment(
            incident_id=incident_id,
            officer_id=best_officer.id,
            assigned_by=assigner_id,
            status="ASSIGNED"
        )
        
        # Log status transition log
        old_status = incident.status
        incident.status = "ASSIGNED"
        
        saved_assignment = self.incident_repo.create_assignment(assignment)
        self.incident_repo.save()

        # Write history transition log
        self.log_status_change(incident_id, old_status, "ASSIGNED", assigner_id, notes=f"Automated spatial workload routing to Officer {best_officer.full_name}")

        # Send in-app notification to officer
        self.notification_service.send_notification(
            user_id=str(best_officer.id),
            title="New Assignment Routed",
            message=f"You have been auto-assigned to incident: {incident.title}",
            notification_type="IN_APP",
            priority="HIGH"
        )

        logger.info(f"AUTO-ASSIGN: Incident {incident_id} auto-routed to Officer {best_officer.id}")
        return saved_assignment

    def check_and_escalate_assignments(self, age_hours: int = 24) -> int:
        """Finds assignments stuck in ASSIGNED status for > age_hours and escalates them."""
        threshold = datetime.now(timezone.utc) - timedelta(hours=age_hours)
        stuck_assignments = db.session.query(Assignment).filter(
            Assignment.status == "ASSIGNED",
            Assignment.created_at <= threshold
        ).all()

        escaped_count = 0
        for assign in stuck_assignments:
            # Send high priority warning notifications to the assigner/staff
            self.notification_service.send_notification(
                user_id=str(assign.assigned_by),
                title="Assignment Escalation Warning",
                message=f"Assignment for Incident '{assign.incident.title}' has not been accepted by Officer in {age_hours} hours. Please manually re-route.",
                notification_type="IN_APP",
                priority="HIGH"
            )
            
            # Log transition warning notes
            self.log_status_change(
                incident_id=str(assign.incident_id),
                status_from=assign.incident.status,
                status_to=assign.incident.status,
                changed_by=str(assign.assigned_by),
                notes=f"SYSTEM WARNING: Assignment stuck for over {age_hours} hours. Escalation notifications dispatched."
            )
            escaped_count += 1

        return escaped_count
