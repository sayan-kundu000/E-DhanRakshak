from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.services.search_service import SearchService
from app.schemas.search_schema import SearchQuerySchema
from app.schemas.incident_schema import IncidentResponseSchema
from app.utils.helpers import paginated_response

search_bp = Blueprint("search", __name__, url_prefix="/api/v1")
search_service = SearchService()

query_schema = SearchQuerySchema()
response_schema = IncidentResponseSchema()

@search_bp.route("/search/incidents", methods=["GET"])
@jwt_required()
def search_incidents():
    """Advanced keyword and parameter filtering search across incidents."""
    validated_args = query_schema.load(request.args)
    
    # Enforce read scopes: Citizens only search their own reported cases
    claims = get_jwt()
    filters = {
        "status": validated_args.get("status"),
        "category": validated_args.get("category"),
        "officer_id": validated_args.get("officer_id"),
        "start_date": validated_args.get("start_date"),
        "end_date": validated_args.get("end_date")
    }
    
    if claims.get("role") == "CITIZEN":
        filters["reporter_id"] = get_jwt_identity()
    else:
        filters["reporter_id"] = validated_args.get("reporter_id")

    records, total = search_service.search_incidents(
        query_str=validated_args.get("q"),
        filters=filters,
        sort_by=validated_args.get("sort_by", "created_at"),
        order=validated_args.get("order", "desc"),
        page=validated_args.get("page", 1),
        limit=validated_args.get("limit", 10)
    )
    
    serialized = response_schema.dump(records, many=True)
    return paginated_response(
        data=serialized,
        total_records=total,
        page=validated_args.get("page", 1),
        limit=validated_args.get("limit", 10),
        message="Search query processed successfully."
    )
