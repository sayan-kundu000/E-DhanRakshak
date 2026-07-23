from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required
from app.services.report_service import ReportService
from app.schemas.report_schema import ReportRequestSchema, ReportResponseSchema
from app.utils.helpers import success_response
from app.middleware.auth_middleware import role_required

report_bp = Blueprint("report", __name__, url_prefix="/api/v1")
report_service = ReportService()

req_schema = ReportRequestSchema()
resp_schema = ReportResponseSchema()

@report_bp.route("/reports/summary", methods=["GET"])
@role_required("ADMINISTRATOR", "STAFF")
def get_report_summary():
    """Returns general count and statistics summaries over a time interval."""
    validated_args = req_schema.load(request.args)
    stats = report_service.get_statistics(validated_args["interval"])
    return success_response(
        data=resp_schema.dump(stats),
        message="Reporting summary retrieved successfully."
    )


@report_bp.route("/reports/export", methods=["GET"])
@role_required("ADMINISTRATOR", "STAFF")
def export_reports():
    """Exports incidents database entries to CSV or text PDF files formats."""
    validated_args = req_schema.load(request.args)
    interval = validated_args["interval"]
    export_format = validated_args.get("format", "csv").lower()

    if export_format == "csv":
        csv_data = report_service.export_csv(interval)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename=report_{interval}.csv"}
        )
    elif export_format == "pdf":
        pdf_data = report_service.export_pdf_mock(interval)
        return Response(
            pdf_data,
            mimetype="application/pdf",
            headers={"Content-disposition": f"attachment; filename=report_{interval}.pdf"}
        )
    else:
        # Defaults to returning JSON raw metrics
        stats = report_service.get_statistics(interval)
        return success_response(data=stats, message="JSON report export.")
