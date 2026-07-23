from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.services.incident_service import IncidentService
from app.schemas.incident_schema import (
    IncidentCreateSchema, IncidentUpdateSchema, IncidentResponseSchema,
    AssignmentCreateSchema, AssignmentUpdateSchema, AssignmentResponseSchema
)
from app.utils.helpers import success_response, paginated_response
from app.middleware.auth_middleware import role_required

incident_bp = Blueprint("incident", __name__, url_prefix="/api/v1")
incident_service = IncidentService()

# Schema Instantiations
create_schema = IncidentCreateSchema()
update_schema = IncidentUpdateSchema()
response_schema = IncidentResponseSchema()
assignment_create_schema = AssignmentCreateSchema()
assignment_update_schema = AssignmentUpdateSchema()
assignment_response_schema = AssignmentResponseSchema()


@incident_bp.route("/incidents", methods=["POST"])
@jwt_required()
def create_incident():
    """Submit a new safety report endpoint."""
    ip_address = request.remote_addr or "127.0.0.1"
    reporter_id = get_jwt_identity()
    
    validated_data = create_schema.load(request.get_json())
    new_incident = incident_service.create_incident(validated_data, reporter_id, ip_address)
    
    return success_response(
        data=response_schema.dump(new_incident),
        message="Incident report submitted successfully.",
        status_code=201
    )


@incident_bp.route("/incidents", methods=["GET"])
@jwt_required()
def list_incidents():
    """Queries, filters, and paginates list of reports."""
    # Build query filters
    filters = {}
    if request.args.get("status"):
        filters["status"] = request.args.get("status")
    if request.args.get("category"):
        filters["category"] = request.args.get("category")
        
    # Standard role checks: Citizens can only see their own tickets
    claims = get_jwt()
    if claims.get("role") == "CITIZEN":
        filters["reporter_id"] = get_jwt_identity()

    # Pagination and sorting parameters
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    sort_by = request.args.get("sort_by", "created_at")
    order = request.args.get("order", "desc")

    records, total = incident_service.list_incidents(filters, sort_by, order, page, limit)
    serialized_data = response_schema.dump(records, many=True)
    
    return paginated_response(
        data=serialized_data,
        total_records=total,
        page=page,
        limit=limit,
        message="Incidents retrieved successfully."
    )


@incident_bp.route("/incidents/<uuid:incident_id>", methods=["GET"])
@jwt_required()
def get_incident(incident_id):
    """Retrieves detailed record of a single incident."""
    incident = incident_service.get_incident(str(incident_id))
    
    # Enforce read restrictions: Citizens cannot inspect other citizens' tickets
    claims = get_jwt()
    if claims.get("role") == "CITIZEN" and str(incident.reporter_id) != get_jwt_identity():
        return success_response(message="Access denied: Resource belongs to another user.", status_code=403)
        
    return success_response(data=response_schema.dump(incident), message="Incident retrieved.")


@incident_bp.route("/incidents/<uuid:incident_id>", methods=["PUT"])
@jwt_required()
def update_incident(incident_id):
    """Updates properties of a report ticket."""
    ip_address = request.remote_addr or "127.0.0.1"
    user_id = get_jwt_identity()
    claims = get_jwt()
    
    validated_data = update_schema.load(request.get_json())
    updated_incident = incident_service.update_incident(
        str(incident_id), 
        validated_data, 
        user_id, 
        claims.get("role"), 
        ip_address
    )
    return success_response(data=response_schema.dump(updated_incident), message="Incident report updated.")


@incident_bp.route("/incidents/<uuid:incident_id>", methods=["DELETE"])
@jwt_required()
def delete_incident(incident_id):
    """Performs soft logical deletion of incident record."""
    ip_address = request.remote_addr or "127.0.0.1"
    user_id = get_jwt_identity()
    claims = get_jwt()
    
    incident_service.delete_incident(str(incident_id), user_id, claims.get("role"), ip_address)
    return success_response(message="Incident report deleted successfully.")


@incident_bp.route("/assignments", methods=["POST"])
@role_required("ADMINISTRATOR", "STAFF")
def assign_officer():
    """Dispatcher maps an officer to target incident report."""
    ip_address = request.remote_addr or "127.0.0.1"
    assigner_id = get_jwt_identity()
    
    validated_data = assignment_create_schema.load(request.get_json())
    new_assignment = incident_service.assign_incident(validated_data, assigner_id, ip_address)
    
    return success_response(
        data=assignment_response_schema.dump(new_assignment),
        message="Incident assigned to officer successfully.",
        status_code=201
    )


@incident_bp.route("/assignments/<uuid:assignment_id>/status", methods=["PUT"])
@role_required("OFFICER")
def update_assignment(assignment_id):
    """Officer responds (accept, reject, resolve) to assignment."""
    ip_address = request.remote_addr or "127.0.0.1"
    officer_id = get_jwt_identity()
    
    validated_data = assignment_update_schema.load(request.get_json())
    updated_assignment = incident_service.update_assignment_status(
        str(assignment_id), 
        validated_data, 
        officer_id, 
        ip_address
    )
    return success_response(
        data=assignment_response_schema.dump(updated_assignment),
        message="Assignment status updated successfully."
    )


@incident_bp.route("/analytics/kpi", methods=["GET"])
@role_required("ADMINISTRATOR", "STAFF")
def get_dashboard_stats():
    """Provides incident metrics counts for management dashboards."""
    stats = incident_service.get_dashboard_kpis()
    return success_response(data=stats, message="Dashboard KPIs retrieved.")


@incident_bp.route("/incidents/<uuid:incident_id>/auto-assign", methods=["POST"])
@role_required("ADMINISTRATOR", "STAFF")
def auto_assign_incident(incident_id):
    """Triggers the workload-approximated spatial auto-assignment workflow."""
    ip_address = request.remote_addr or "127.0.0.1"
    assigner_id = get_jwt_identity()
    
    from app.services.workflow_service import WorkflowService
    workflow_service = WorkflowService()
    new_assignment = workflow_service.auto_assign_incident(str(incident_id), assigner_id, ip_address)
    
    return success_response(
        data=assignment_response_schema.dump(new_assignment),
        message="Incident auto-assigned to best available officer successfully.",
        status_code=201
    )

