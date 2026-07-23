import csv
import io
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from sqlalchemy import func
from app.extensions import db
from app.models.incident import Incident
from app.middleware.error_handler import ValidationError

class ReportService:
    """Orchestrates structured safety incident statistics auditing and file formats generation."""

    def _get_date_range(self, interval: str) -> datetime:
        """Determines the start UTC datetime bound from the provided interval."""
        now = datetime.now(timezone.utc)
        if interval == "daily":
            return now - timedelta(days=1)
        elif interval == "weekly":
            return now - timedelta(days=7)
        elif interval == "monthly":
            return now - timedelta(days=30)
        elif interval == "yearly":
            return now - timedelta(days=365)
        else:
            raise ValidationError(f"Invalid reporting interval '{interval}'. Use 'daily', 'weekly', 'monthly', or 'yearly'.")

    def get_statistics(self, interval: str) -> Dict[str, Any]:
        start_date = self._get_date_range(interval)

        # 1. Fetch counts grouped by category
        categories = db.session.query(
            Incident.category, func.count(Incident.id)
        ).filter(
            Incident.created_at >= start_date,
            Incident.is_deleted == False
        ).group_by(Incident.category).all()
        categories_dict = {cat: count for cat, count in categories}

        # 2. Fetch counts grouped by status
        statuses = db.session.query(
            Incident.status, func.count(Incident.id)
        ).filter(
            Incident.created_at >= start_date,
            Incident.is_deleted == False
        ).group_by(Incident.status).all()
        statuses_dict = {stat: count for stat, count in statuses}

        # 3. Aggregates
        aggregates = db.session.query(
            func.count(Incident.id).label("total")
        ).filter(
            Incident.created_at >= start_date,
            Incident.is_deleted == False
        ).first()

        total_count = aggregates[0] if aggregates else 0

        # Calculate average risk score
        from app.models.incident import RiskAssessment
        avg_risk = db.session.query(
            func.avg(RiskAssessment.risk_score)
        ).join(
            Incident, Incident.id == RiskAssessment.incident_id
        ).filter(
            Incident.created_at >= start_date,
            Incident.is_deleted == False
        ).scalar()

        avg_risk_val = float(avg_risk) if avg_risk is not None else 0.0

        return {
            "interval": interval,
            "start_date": start_date.isoformat(),
            "total_incidents": total_count,
            "average_risk_score": round(avg_risk_val, 2),
            "by_category": categories_dict,
            "by_status": statuses_dict
        }

    def export_csv(self, interval: str) -> str:
        start_date = self._get_date_range(interval)
        incidents = db.session.query(Incident).filter(
            Incident.created_at >= start_date,
            Incident.is_deleted == False
        ).order_by(Incident.created_at.desc()).all()

        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(["ID", "Title", "Category", "Status", "Latitude", "Longitude", "Created At"])
        for inc in incidents:
            writer.writerow([
                str(inc.id),
                inc.title,
                inc.category,
                inc.status,
                float(inc.latitude),
                float(inc.longitude),
                inc.created_at.isoformat()
            ])
            
        return output.getvalue()

    def export_pdf_mock(self, interval: str) -> bytes:
        stats = self.get_statistics(interval)
        
        # Build a beautifully formatted text report that simulates a PDF summary
        pdf_text = f"""
========================================================================
                      E-DHANRAKSHAK SAFETY REPORT SUMMARY
========================================================================
Interval: {stats['interval'].upper()}
Report Generated At: {datetime.now(timezone.utc).isoformat()}
Start Date Threshold: {stats['start_date']}
------------------------------------------------------------------------
TOTAL INCIDENTS LOGGED: {stats['total_incidents']}
AVERAGE RISK INDEX SCORE: {stats['average_risk_score']} / 100.00
------------------------------------------------------------------------
INCIDENTS BY CATEGORY:
"""
        for cat, count in stats["by_category"].items():
            pdf_text += f"  - {cat}: {count}\n"

        pdf_text += "\nINCIDENTS BY STATUS:\n"
        for status, count in stats["by_status"].items():
            pdf_text += f"  - {status}: {count}\n"

        pdf_text += "\n========================================================================\n"
        
        return pdf_text.encode("utf-8")
