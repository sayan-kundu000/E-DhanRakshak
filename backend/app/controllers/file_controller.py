from flask import Blueprint, request, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.file_service import FileService
from app.schemas.file_schema import FileAttachmentResponseSchema
from app.utils.helpers import success_response
from app.middleware.error_handler import ValidationError

file_bp = Blueprint("file", __name__, url_prefix="/api/v1")
file_service = FileService()
file_response_schema = FileAttachmentResponseSchema()

@file_bp.route("/files/upload", methods=["POST"])
@jwt_required()
def upload_file():
    """Endpoint for uploading incident attachments and reports."""
    if "file" not in request.files:
        raise ValidationError("No file field provided in multipart form-data.")
    
    uploaded_file = request.files["file"]
    owner_id = get_jwt_identity()
    
    attachment = file_service.upload_file(uploaded_file, owner_id)
    return success_response(
        data=file_response_schema.dump(attachment),
        message="File uploaded successfully.",
        status_code=201
    )


@file_bp.route("/files/download/<string:stored_name>", methods=["GET"])
@jwt_required()
def download_file(stored_name):
    """Secure file download stream route checking auth token validation."""
    # Find metadata
    file_record = file_service.get_file_by_name(stored_name)
    
    # Secure download stream
    return send_from_directory(
        directory=current_app.config["UPLOAD_FOLDER"],
        path=file_record.stored_name,
        as_attachment=True,
        download_name=file_record.original_name
    )


@file_bp.route("/files/<uuid:file_id>", methods=["DELETE"])
@jwt_required()
def delete_file(file_id):
    """Logical soft delete endpoint for attachments."""
    user_id = get_jwt_identity()
    claims = get_jwt()
    
    file_service.delete_file(str(file_id), user_id, claims.get("role"))
    return success_response(message="File attachment deleted successfully.")
