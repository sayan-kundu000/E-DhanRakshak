from typing import Dict, Any, Tuple, List, Optional
from sqlalchemy import or_
from app.extensions import db
from app.models.incident import Incident, Assignment

class SearchService:
    """Orchestrates global keyword searches and advanced filtered lists queries."""

    def search_incidents(
        self,
        query_str: Optional[str] = None,
        filters: Optional[dict] = None,
        sort_by: str = "created_at",
        order: str = "desc",
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[Incident], int]:
        query = db.session.query(Incident).filter(Incident.is_deleted == False)
        filters = filters or {}

        # 1. Apply global keyword search across title and description
        if query_str:
            search_term = f"%{query_str.strip()}%"
            query = query.filter(or_(
                Incident.title.ilike(search_term),
                Incident.description.ilike(search_term)
            ))

        # 2. Apply advanced filters
        if "status" in filters and filters["status"]:
            query = query.filter(Incident.status == filters["status"])
        if "category" in filters and filters["category"]:
            query = query.filter(Incident.category == filters["category"])
        if "reporter_id" in filters and filters["reporter_id"]:
            query = query.filter(Incident.reporter_id == filters["reporter_id"])
            
        # Support searching by officer_id (requires joining assignments table)
        if "officer_id" in filters and filters["officer_id"]:
            query = query.join(Assignment, Incident.id == Assignment.incident_id).filter(
                Assignment.officer_id == filters["officer_id"]
            )

        if "start_date" in filters and filters["start_date"]:
            query = query.filter(Incident.created_at >= filters["start_date"])
        if "end_date" in filters and filters["end_date"]:
            query = query.filter(Incident.created_at <= filters["end_date"])

        # Total counts
        total_records = query.count()

        # Apply sorting
        sort_col = getattr(Incident, sort_by, Incident.created_at)
        if order.lower() == "asc":
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(sort_col.desc())

        # Offset paging
        records = query.offset((page - 1) * limit).limit(limit).all()

        return records, total_records
