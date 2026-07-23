from flask import Blueprint, request, Response, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.services.dashboard_service import DashboardService
from app.services.analytics_service import AnalyticsService
from app.services.prediction_service import PredictionService
from app.schemas.analytics_schema import PredictionRequestSchema, ChartQuerySchema
from app.utils.helpers import success_response
from app.middleware.error_handler import ValidationError

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/v1/analytics")

dashboard_service = DashboardService()
analytics_service = AnalyticsService()
prediction_service = PredictionService()

pred_req_schema = PredictionRequestSchema()
chart_query_schema = ChartQuerySchema()

@analytics_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def get_dashboard():
    """Retrieves operational counts and timelines customized per user role."""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role", "CITIZEN")

    if role in ["ADMINISTRATOR", "STAFF"]:
        data = dashboard_service.get_admin_dashboard()
    elif role == "OFFICER":
        data = dashboard_service.get_officer_dashboard(user_id)
    else:
        data = dashboard_service.get_citizen_dashboard(user_id)

    return success_response(data=data, message="Dashboard metrics compiled.")


@analytics_bp.route("/prediction", methods=["GET"])
@jwt_required()
def predict_metrics():
    """Predicts resolution duration and priority mapping for a hypothetical incident."""
    validated_args = pred_req_schema.load(request.args)
    
    pred_data = prediction_service.predict_incident_metrics(
        category=validated_args["category"],
        lat=validated_args["latitude"],
        lon=validated_args["longitude"],
        timestamp=validated_args.get("timestamp")
    )
    return success_response(data=pred_data, message="Prediction completed successfully.")


@analytics_bp.route("/trends", methods=["GET"])
@jwt_required()
def get_trends():
    """Retrieves 7-day rolling average and growth rate analysis."""
    trends = analytics_service.calculate_growth_and_trends()
    return success_response(data=trends, message="Historical trends compiled.")


@analytics_bp.route("/charts/<string:chart_name>", methods=["GET"])
@jwt_required()
def get_chart(chart_name):
    """Generates and streams category/trend distributions in Plotly or Matplotlib format."""
    validated_args = chart_query_schema.load(request.args)
    chart_format = validated_args["format"]

    if chart_name not in ["category", "trend"]:
        raise ValidationError(f"Invalid chart name '{chart_name}'. Use 'category' or 'trend'.")

    if chart_format == "png":
        if chart_name == "category":
            img_bytes = analytics_service.generate_category_matplotlib_chart()
        else:
            img_bytes = analytics_service.generate_trend_matplotlib_chart()
        return Response(img_bytes, mimetype="image/png")
    else:
        # Default to interactive Plotly layout JSON dict
        if chart_name == "category":
            chart_json = analytics_service.generate_category_plotly_chart()
        else:
            chart_json = analytics_service.generate_trend_plotly_chart()
        return success_response(data=chart_json, message="Plotly chart layout compiled.")
