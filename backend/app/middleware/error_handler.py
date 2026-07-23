import logging
from flask import jsonify
from marshmallow import ValidationError as MarshmallowValidationError
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended.exceptions import JWTExtendedException
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

class AppException(Exception):
    """Base application exception for E-DhanRakshak custom business error logic."""
    def __init__(self, message, status_code=400, code="APP_ERROR", details=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details


class ValidationError(AppException):
    """Exception raised when payload validations or business check constraints fail."""
    def __init__(self, message="Validation failed", details=None):
        super().__init__(message, status_code=400, code="VALIDATION_FAILED", details=details)


class AuthError(AppException):
    """Exception raised on invalid signatures, missing credentials, or insufficient permissions."""
    def __init__(self, message="Unauthorized access", status_code=401, code="UNAUTHORIZED"):
        super().__init__(message, status_code=status_code, code=code)


class ResourceNotFoundError(AppException):
    """Exception raised when UUID entities or configuration keys cannot be resolved."""
    def __init__(self, message="Resource not found"):
        super().__init__(message, status_code=404, code="RESOURCE_NOT_FOUND")


class DuplicateResourceError(AppException):
    """Exception raised when registering an email or checksum which already exists."""
    def __init__(self, message="Resource already exists"):
        super().__init__(message, status_code=409, code="DUPLICATE_RESOURCE")


class BusinessRuleError(AppException):
    """Exception raised when workflows violate state constraints or rules."""
    def __init__(self, message="Business rule violation"):
        super().__init__(message, status_code=422, code="BUSINESS_RULE_VIOLATION")


class StorageError(AppException):
    """Exception raised when writing or reading from file storage fails."""
    def __init__(self, message="Storage operation failed"):
        super().__init__(message, status_code=500, code="STORAGE_ERROR")


class ConfigurationError(AppException):
    """Exception raised on invalid feature flags or missing configurations."""
    def __init__(self, message="Configuration error"):
        super().__init__(message, status_code=500, code="CONFIGURATION_ERROR")


class ExternalServiceError(AppException):
    """Exception raised when notification or analytics services fail."""
    def __init__(self, message="External service error"):
        super().__init__(message, status_code=502, code="BAD_GATEWAY")



def register_error_handlers(app):
    """Registers exception mappings onto the Flask application object."""
    
    @app.errorhandler(AppException)
    def handle_custom_app_exception(error):
        payload = {
            "success": False,
            "error": {
                "code": error.code,
                "message": error.message,
                "details": error.details
            }
        }
        return jsonify(payload), error.status_code

    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_validation(error):
        payload = {
            "success": False,
            "error": {
                "code": "VALIDATION_FAILED",
                "message": "Input validation failed.",
                "details": error.messages
            }
        }
        return jsonify(payload), 400

    @app.errorhandler(JWTExtendedException)
    def handle_jwt_exceptions(error):
        logger.warning(f"JWT signature or validation error intercept: {str(error)}")
        payload = {
            "success": False,
            "error": {
                "code": "UNAUTHORIZED",
                "message": str(error),
                "details": None
            }
        }
        return jsonify(payload), 401

    @app.errorhandler(SQLAlchemyError)
    def handle_database_errors(error):
        logger.error(f"Database SQL execution error: {str(error)}", exc_info=True)
        payload = {
            "success": False,
            "error": {
                "code": "DATABASE_ERROR",
                "message": "A database connection or transaction error occurred.",
                "details": None
            }
        }
        return jsonify(payload), 500

    @app.errorhandler(HTTPException)
    def handle_standard_http_exceptions(error):
        payload = {
            "success": False,
            "error": {
                "code": "HTTP_ERROR",
                "message": error.description,
                "details": None
            }
        }
        return jsonify(payload), error.code

    @app.errorhandler(Exception)
    def handle_unhandled_exceptions(error):
        logger.error(f"Unhandled system error: {str(error)}", exc_info=True)
        payload = {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred on the server.",
                "details": None
            }
        }
        return jsonify(payload), 500
