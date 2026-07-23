from typing import Dict, Any, List
from sqlalchemy import func
from app.extensions import db
from app.models.incident import Incident, Assignment, RiskAssessment
from app.models.user import User
from app.models.workflow import IncidentHistory
from app.models.user import AuditLog

class DashboardService:
    """Orchestrates compilation of role-based KPIs, active workloads, and audit timelines."""

    def get_citizen_dashboard(self, citizen_id: str) -> Dict[str, Any]:
        """Compiles personal metrics for the logged-in citizen."""
        total = db.session.query(Incident).filter(
            Incident.reporter_id == citizen_id,
            Incident.is_deleted == False
        ).count()

        resolved = db.session.query(Incident).filter(
            Incident.reporter_id == citizen_id,
            Incident.status == "RESOLVED",
            Incident.is_deleted == False
        ).count()

        open_cases = total - resolved

        # Recent activities (last 5 status changes on their tickets)
        recent_changes = db.session.query(IncidentHistory).join(
            Incident, Incident.id == IncidentHistory.incident_id
        ).filter(
            Incident.reporter_id == citizen_id
        ).order_by(IncidentHistory.created_at.desc()).limit(5).all()

        timeline = [{
            "incident_id": str(h.incident_id),
            "status_from": h.status_from,
            "status_to": h.status_to,
            "notes": h.notes,
            "created_at": h.created_at.isoformat()
        } for h in recent_changes]

        return {
            "role": "CITIZEN",
            "kpis": {
                "total_reported": total,
                "resolved_count": resolved,
                "active_count": open_cases,
                "resolution_rate": round((resolved / total * 100), 2) if total > 0 else 0.0
            },
            "recent_activity": timeline
        }

    def get_officer_dashboard(self, officer_id: str) -> Dict[str, Any]:
        """Compiles active assignments, workload, and timeline metrics for the designated officer."""
        total_assignments = db.session.query(Assignment).filter(
            Assignment.officer_id == officer_id
        ).count()

        resolved = db.session.query(Assignment).filter(
            Assignment.officer_id == officer_id,
            Assignment.status == "RESOLVED"
        ).count()

        pending_assigned = db.session.query(Assignment).filter(
            Assignment.officer_id == officer_id,
            Assignment.status == "ASSIGNED"
        ).count()

        pending_accepted = db.session.query(Assignment).filter(
            Assignment.officer_id == officer_id,
            Assignment.status == "ACCEPTED"
        ).count()

        # Average risk score of assigned incidents
        avg_risk = db.session.query(
            func.avg(RiskAssessment.risk_score)
        ).join(
            Incident, Incident.id == RiskAssessment.incident_id
        ).join(
            Assignment, Assignment.incident_id == Incident.id
        ).filter(
            Assignment.officer_id == officer_id
        ).scalar()

        avg_risk_val = float(avg_risk) if avg_risk is not None else 0.0

        # Recent assignments (last 5)
        recent_assigns = db.session.query(Assignment).filter(
            Assignment.officer_id == officer_id
        ).order_by(Assignment.created_at.desc()).limit(5).all()

        timeline = [{
            "assignment_id": str(a.id),
            "incident_id": str(a.incident_id),
            "incident_title": a.incident.title if a.incident else "Unknown",
            "status": a.status,
            "assigned_at": a.created_at.isoformat()
        } for a in recent_assigns]

        return {
            "role": "OFFICER",
            "kpis": {
                "total_assigned": total_assignments,
                "resolved_count": resolved,
                "pending_action": pending_assigned,
                "in_progress": pending_accepted,
                "average_risk_score": round(avg_risk_val, 2),
                "resolution_rate": round((resolved / total_assignments * 100), 2) if total_assignments > 0 else 0.0
            },
            "recent_assignments": timeline
        }

    def get_admin_dashboard(self) -> Dict[str, Any]:
        """Compiles overall system utilization, workload counts, and high-risk case flags."""
        total_incidents = db.session.query(Incident).filter(Incident.is_deleted == False).count()
        resolved = db.session.query(Incident).filter(
            Incident.status == "RESOLVED",
            Incident.is_deleted == False
        ).count()
        active = total_incidents - resolved

        avg_risk = db.session.query(func.avg(RiskAssessment.risk_score)).scalar()
        avg_risk_val = float(avg_risk) if avg_risk is not None else 0.0

        # Officers workload list (active assignments counts)
        officers = db.session.query(User).filter(
            User.role == "OFFICER",
            User.is_active == True,
            User.is_deleted == False
        ).all()

        workloads = []
        for off in officers:
            active_count = db.session.query(Assignment).filter(
                Assignment.officer_id == off.id,
                Assignment.status.in_(["ASSIGNED", "ACCEPTED"])
            ).count()
            workloads.append({
                "officer_id": str(off.id),
                "officer_name": off.full_name,
                "active_assignments": active_count
            })

        # Top 5 high risk pending cases
        high_risk_cases = db.session.query(Incident).join(
            RiskAssessment, Incident.id == RiskAssessment.incident_id
        ).filter(
            Incident.status.in_(["SUBMITTED", "ASSIGNED", "IN_PROGRESS"]),
            Incident.is_deleted == False
        ).order_by(RiskAssessment.risk_score.desc()).limit(5).all()

        cases_list = [{
            "incident_id": str(c.id),
            "title": c.title,
            "category": c.category,
            "status": c.status,
            "risk_score": float(c.risk_assessment.risk_score) if c.risk_assessment else 0.0,
            "created_at": c.created_at.isoformat()
        } for c in high_risk_cases]

        return {
            "role": "ADMINISTRATOR",
            "kpis": {
                "total_logged": total_incidents,
                "resolved_count": resolved,
                "active_count": active,
                "average_risk_score": round(avg_risk_val, 2),
                "resolution_rate": round((resolved / total_incidents * 100), 2) if total_incidents > 0 else 0.0
            },
            "officers_workload": workloads,
            "critical_pending_cases": cases_list
        }
