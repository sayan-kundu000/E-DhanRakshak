from typing import List
from app.extensions import db
from app.models.workflow import IncidentHistory

class WorkflowRepository:
    """Encapsulates status transitions logging and audits history query methods."""

    def create_history_log(self, log: IncidentHistory) -> IncidentHistory:
        db.session.add(log)
        db.session.flush()
        return log

    def get_incident_history(self, incident_id: str) -> List[IncidentHistory]:
        return db.session.query(IncidentHistory).filter(
            IncidentHistory.incident_id == incident_id
        ).order_by(IncidentHistory.created_at.asc()).all()

    def save(self):
        db.session.commit()
