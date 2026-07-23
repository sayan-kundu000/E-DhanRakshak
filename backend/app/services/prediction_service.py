import os
import pickle
import logging
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from app.extensions import db
from app.models.incident import Incident
from app.models.incident import RiskAssessment

logger = logging.getLogger("app.analytics")

CATEGORY_MAP = {
    "THEFT": 0,
    "ASSAULT": 1,
    "FIRE": 2,
    "ACCIDENT": 3,
    "VANDALISM": 4,
    "OTHER": 5
}

REVERSE_PRIORITY_MAP = {
    1: "LOW",
    2: "MEDIUM",
    3: "HIGH"
}

class PredictionService:
    """Orchestrates scikit-learn models training and runtime inference for priority and resolution duration prediction."""

    def __init__(self, model_dir: str = None):
        self._model_dir = model_dir

    @property
    def model_dir(self) -> str:
        if self._model_dir:
            return self._model_dir
        from flask import current_app
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], "models")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @property
    def classifier_path(self) -> str:
        return os.path.join(self.model_dir, "priority_clf.pkl")

    @property
    def regressor_path(self) -> str:
        return os.path.join(self.model_dir, "duration_reg.pkl")

    def _get_baseline_priority(self, category: str) -> str:
        """Rule-based priority fallback selection."""
        if category in ["FIRE", "ASSAULT"]:
            return "HIGH"
        elif category in ["ACCIDENT", "THEFT"]:
            return "MEDIUM"
        else:
            return "LOW"

    def _get_baseline_duration(self, category: str) -> float:
        """Rule-based resolution time duration hours fallback."""
        durations = {
            "FIRE": 2.0,
            "ASSAULT": 6.0,
            "ACCIDENT": 8.0,
            "THEFT": 24.0,
            "VANDALISM": 36.0,
            "OTHER": 48.0
        }
        return durations.get(category, 24.0)

    def train_models(self) -> dict:
        """Queries historical resolved incidents to train classifier and regressor models."""
        logger.info("Training predictive ML models...")
        
        # 1. Fetch resolved incidents
        resolved_incidents = db.session.query(Incident).filter(
            Incident.status == "RESOLVED",
            Incident.is_deleted == False
        ).all()

        if len(resolved_incidents) < 10:
            logger.info(f"Insufficient training data count ({len(resolved_incidents)}/10). Skipping ML training.")
            return {"status": "SKIPPED", "reason": "Insufficient data"}

        # 2. Extract features and targets
        data_rows = []
        for inc in resolved_incidents:
            # Calculate duration in hours
            duration = (inc.updated_at - inc.created_at).total_seconds() / 3600.0
            
            # Map priority classification based on risk score or baseline rules
            risk_score = float(inc.risk_assessment.risk_score) if inc.risk_assessment else 50.0
            if risk_score >= 70.0:
                priority_class = 3  # HIGH
            elif risk_score >= 40.0:
                priority_class = 2  # MEDIUM
            else:
                priority_class = 1  # LOW

            cat_code = CATEGORY_MAP.get(inc.category, 5)
            hour = inc.created_at.hour
            day_of_week = inc.created_at.weekday()

            data_rows.append({
                "cat_code": cat_code,
                "latitude": float(inc.latitude),
                "longitude": float(inc.longitude),
                "hour": hour,
                "day_of_week": day_of_week,
                "priority": priority_class,
                "duration": duration
            })

        df = pd.DataFrame(data_rows)

        X = df[["cat_code", "latitude", "longitude", "hour", "day_of_week"]]
        y_clf = df["priority"]
        y_reg = df["duration"]

        try:
            # 3. Train models
            clf = RandomForestClassifier(n_estimators=50, random_state=42)
            clf.fit(X, y_clf)

            reg = RandomForestRegressor(n_estimators=50, random_state=42)
            reg.fit(X, y_reg)

            # 4. Save models
            with open(self.classifier_path, "wb") as f:
                pickle.dump(clf, f)
            with open(self.regressor_path, "wb") as f:
                pickle.dump(reg, f)

            logger.info("Predictive models successfully trained and serialized.")
            return {"status": "SUCCESS", "trained_records": len(resolved_incidents)}
        except Exception as e:
            logger.error(f"Error training machine learning models: {str(e)}", exc_info=True)
            return {"status": "FAILED", "error": str(e)}

    def predict_incident_metrics(self, category: str, lat: float, lon: float, timestamp: datetime = None) -> dict:
        """Predicts incident resolution duration and priority mapping (model-based or rule-based fallback)."""
        timestamp = timestamp or datetime.now(timezone.utc)
        cat_code = CATEGORY_MAP.get(category, 5)
        hour = timestamp.hour
        day_of_week = timestamp.weekday()

        # Check if trained models exist
        if os.path.exists(self.classifier_path) and os.path.exists(self.regressor_path):
            try:
                with open(self.classifier_path, "rb") as f:
                    clf = pickle.load(f)
                with open(self.regressor_path, "rb") as f:
                    reg = pickle.load(f)

                # Prepare feature vector
                features = np.array([[cat_code, float(lat), float(lon), hour, day_of_week]])

                # Predict priority class
                pred_priority_class = int(clf.predict(features)[0])
                priority = REVERSE_PRIORITY_MAP.get(pred_priority_class, "MEDIUM")

                # Predict duration in hours
                pred_duration = float(reg.predict(features)[0])

                return {
                    "priority": priority,
                    "predicted_duration_hours": round(pred_duration, 2),
                    "confidence_score": 0.85,
                    "method": "MACHINE_LEARNING"
                }
            except Exception as e:
                logger.warning(f"Error during ML model inference: {str(e)}. Falling back to rules engine.")
        
        # Fallback rule-based estimation
        priority = self._get_baseline_priority(category)
        duration = self._get_baseline_duration(category)

        return {
            "priority": priority,
            "predicted_duration_hours": round(duration, 2),
            "confidence_score": 0.50,
            "method": "RULES_ENGINE"
        }
