import os
import uuid
from datetime import datetime, timezone
from flask import jsonify

def get_utc_now() -> datetime:
    """Returns the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime) -> str:
    """Standardizes datetime serialization format to ISO 8601 strings."""
    if not dt:
        return ""
    return dt.isoformat()


def generate_uuid_string() -> str:
    """Generates a secure random UUIDv4 string."""
    return str(uuid.uuid4())


def is_allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Returns True if the file extension is matches allowed extensions sets."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in allowed_extensions


def success_response(data=None, message="Operation completed successfully.", status_code=200):
    """Builds standard success JSON envelopes."""
    payload = {
        "success": True,
        "data": data,
        "message": message
    }
    return jsonify(payload), status_code


def error_response(code="API_ERROR", message="An error occurred.", details=None, status_code=400):
    """Builds standard error JSON envelopes."""
    payload = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details
        }
    }
    return jsonify(payload), status_code


def paginated_response(data, total_records, page, limit, message="Records retrieved."):
    """Builds standard paginated data envelopes."""
    total_pages = (total_records + limit - 1) // limit if limit > 0 else 0
    payload = {
        "success": True,
        "data": data,
        "pagination": {
            "total_records": total_records,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "message": message
    }
    return jsonify(payload), 200
