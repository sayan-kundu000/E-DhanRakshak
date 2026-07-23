from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

from app.services.auth_service import AuthService
from app.schemas.auth_schema import (
    RegisterSchema, LoginSchema, ProfileUpdateSchema, 
    ChangePasswordSchema, UserResponseSchema
)
from app.utils.helpers import success_response
from app.middleware.auth_middleware import role_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
auth_service = AuthService()

# Schema Instantiations
register_schema = RegisterSchema()
login_schema = LoginSchema()
profile_update_schema = ProfileUpdateSchema()
change_password_schema = ChangePasswordSchema()
user_response_schema = UserResponseSchema()


@auth_bp.route("/register", methods=["POST"])
def register():
    """User self-registration API endpoint."""
    ip_address = request.remote_addr or "127.0.0.1"
    validated_data = register_schema.load(request.get_json())
    
    new_user = auth_service.register_user(validated_data, ip_address)
    
    return success_response(
        data=user_response_schema.dump(new_user), 
        message="User account registered successfully.", 
        status_code=201
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    """JWT credential login validation API endpoint."""
    ip_address = request.remote_addr or "127.0.0.1"
    validated_data = login_schema.load(request.get_json())
    
    access_token, refresh_token, user = auth_service.login_user(validated_data, ip_address)
    
    response_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user_response_schema.dump(user)
    }
    return success_response(data=response_data, message="Authentication successful.")


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Reissues short-lived access tokens using active refresh tokens."""
    current_user_id = get_jwt_identity()
    user = auth_service.get_profile(current_user_id)
    
    new_access_token = create_access_token(
        identity=str(user.id), 
        additional_claims={"role": user.role}
    )
    return success_response(
        data={"access_token": new_access_token}, 
        message="Access token refreshed successfully."
    )


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Returns profile details of the currently authenticated session."""
    current_user_id = get_jwt_identity()
    user = auth_service.get_profile(current_user_id)
    return success_response(data=user_response_schema.dump(user), message="Profile retrieved.")


@auth_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_current_user():
    """Updates profile properties of the current user session."""
    ip_address = request.remote_addr or "127.0.0.1"
    current_user_id = get_jwt_identity()
    validated_data = profile_update_schema.load(request.get_json())
    
    updated_user = auth_service.update_profile(current_user_id, validated_data, ip_address)
    return success_response(data=user_response_schema.dump(updated_user), message="Profile updated successfully.")


@auth_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    """Updates password checking matching current password verification payload."""
    ip_address = request.remote_addr or "127.0.0.1"
    current_user_id = get_jwt_identity()
    validated_data = change_password_schema.load(request.get_json())
    
    auth_service.change_password(current_user_id, validated_data, ip_address)
    return success_response(message="Password updated successfully.")


@auth_bp.route("/users/<uuid:user_id>/activation", methods=["PUT"])
@role_required("ADMINISTRATOR")
def toggle_activation(user_id):
    """Enables Administrators to toggle user accounts is_active state levels."""
    ip_address = request.remote_addr or "127.0.0.1"
    admin_id = get_jwt_identity()
    
    payload = request.get_json() or {}
    is_active = payload.get("is_active")
    
    if is_active is None:
        return success_response(message="is_active parameter missing.", status_code=400)
        
    updated_user = auth_service.toggle_user_activation(
        str(user_id), 
        bool(is_active), 
        admin_id, 
        ip_address
    )
    
    state_msg = "activated" if is_active else "deactivated"
    return success_response(
        data=user_response_schema.dump(updated_user),
        message=f"User account successfully {state_msg}."
    )
