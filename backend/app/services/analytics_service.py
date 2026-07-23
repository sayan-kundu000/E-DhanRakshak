import io
import logging
import matplotlib
matplotlib.use('Agg')  # Headless non-interactive thread-safe backend
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import func
from app.extensions import db
from app.models.incident import Incident
from app.models.incident import RiskAssessment

logger = logging.getLogger("app.analytics")

class AnalyticsService:
    """Orchestrates statistical queries, moving averages, growth analysis, and Plotly/Matplotlib charts generation."""

    def calculate_growth_and_trends(self) -> Dict[str, Any]:
        """Calculates 7-day rolling average and growth rate comparisons."""
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=30)

        # 1. Query daily counts for the last 30 days
        daily_query = db.session.query(
            func.date(Incident.created_at).label("day"),
            func.count(Incident.id).label("count")
        ).filter(
            Incident.created_at >= start_date,
            Incident.is_deleted == False
        ).group_by(func.date(Incident.created_at)).all()

        daily_data = {str(d.day): d.count for d in daily_query}

        # 2. Build full range index to fill in missing days with 0 counts
        date_index = [str((start_date + timedelta(days=i)).date()) for i in range(31)]
        counts = [daily_data.get(dt, 0) for dt in date_index]

        df = pd.DataFrame({"date": date_index, "count": counts})
        
        # Calculate 7-day rolling average
        df["rolling_avg"] = df["count"].rolling(window=7, min_periods=1).mean()

        # 3. Calculate growth rate (current 7 days vs previous 7 days)
        current_7_count = df["count"].tail(7).sum()
        prev_7_count = df["count"].iloc[-14:-7].sum()

        growth_rate = 0.0
        if prev_7_count > 0:
            growth_rate = round(((current_7_count - prev_7_count) / prev_7_count) * 100, 2)
        elif current_7_count > 0:
            growth_rate = 100.0  # Infinite growth baseline

        return {
            "dates": df["date"].tolist(),
            "daily_counts": df["count"].tolist(),
            "rolling_averages": [round(float(val), 2) for val in df["rolling_avg"].tolist()],
            "growth_rate_percent": growth_rate,
            "current_week_total": int(current_7_count),
            "previous_week_total": int(prev_7_count)
        }

    def generate_category_plotly_chart(self) -> dict:
        """Generates category distribution layout via Plotly."""
        categories = db.session.query(
            Incident.category, func.count(Incident.id)
        ).filter(
            Incident.is_deleted == False
        ).group_by(Incident.category).all()

        labels = [cat[0] for cat in categories]
        values = [cat[1] for cat in categories]

        if not labels:
            labels = ["No Data"]
            values = [0]

        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
        fig.update_layout(title_text="Incidents Distribution by Category")
        return fig.to_dict()

    def generate_category_matplotlib_chart(self) -> bytes:
        """Generates category distribution layout PNG bytes via Matplotlib."""
        categories = db.session.query(
            Incident.category, func.count(Incident.id)
        ).filter(
            Incident.is_deleted == False
        ).group_by(Incident.category).all()

        labels = [cat[0] for cat in categories]
        values = [cat[1] for cat in categories]

        # Reset plot layout states
        plt.clf()
        plt.figure(figsize=(6, 4))
        
        if not labels:
            plt.text(0.5, 0.5, "No Data Available", ha="center", va="center")
        else:
            plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=["#3f51b5", "#f44336", "#ff9800", "#4caf50", "#9c27b0", "#795548"])
            plt.title("Incidents by Category")

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        plt.close()
        return buf.getvalue()

    def generate_trend_plotly_chart(self) -> dict:
        """Generates incident trend timeline layout via Plotly."""
        trends = self.calculate_growth_and_trends()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=trends["dates"], y=trends["daily_counts"], name="Daily Logged"))
        fig.add_trace(go.Scatter(x=trends["dates"], y=trends["rolling_averages"], name="7-Day Moving Avg", line=dict(color='firebrick', width=3)))
        
        fig.update_layout(title="Incident Trend & Moving Average", xaxis_title="Date", yaxis_title="Counts")
        return fig.to_dict()

    def generate_trend_matplotlib_chart(self) -> bytes:
        """Generates incident trend timeline layout PNG bytes via Matplotlib."""
        trends = self.calculate_growth_and_trends()

        plt.clf()
        plt.figure(figsize=(8, 4))
        
        # Convert date strings to clean visual format if possible
        x = trends["dates"]
        y_daily = trends["daily_counts"]
        y_avg = trends["rolling_averages"]

        plt.bar(x, y_daily, color="#b39ddb", label="Daily Logged")
        plt.plot(x, y_avg, color="#673ab7", linewidth=2.5, label="7-Day Moving Avg")
        
        plt.xlabel("Date")
        plt.ylabel("Counts")
        plt.title("Incident Trend & Moving Average")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()
        return buf.getvalue()
