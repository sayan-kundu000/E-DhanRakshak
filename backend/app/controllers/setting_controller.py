from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.setting_service import SettingService
from app.schemas.setting_schema import SystemSettingResponseSchema, SystemSettingUpdateSchema, UserPreferenceSchema
from app.utils.helpers import success_response
from app.middleware.auth_middleware import role_required

setting_bp = Blueprint("setting", __name__, url_prefix="/api/v1")
setting_service = SettingService()

setting_response_schema = SystemSettingResponseSchema()
setting_update_schema = SystemSettingUpdateSchema()
pref_schema = UserPreferenceSchema()

@setting_bp.route("/settings", methods=["GET"])
@jwt_required()
def list_system_settings():
    """Lists system configurations."""
    category = request.args.get("category")
    records = setting_service.list_system_settings(category)
    return success_response(
        data=setting_response_schema.dump(records, many=True),
        message="System settings retrieved."
    )


@setting_bp.route("/settings/<string:key>", methods=["GET"])
@jwt_required()
def get_system_setting(key):
    """Retrieves value of a specific setting key."""
    setting = setting_service.get_system_setting(key)
    return success_response(
        data=setting_response_schema.dump(setting),
        message="System setting retrieved."
    )


@setting_bp.route("/settings/<string:key>", methods=["PUT"])
@role_required("ADMINISTRATOR")
def update_system_setting(key):
    """Enables administrators to write/overwrite a configuration variable."""
    validated_data = setting_update_schema.load(request.get_json())
    setting = setting_service.set_system_setting(
        key=key,
        value=validated_data["value"],
        description=validated_data.get("description"),
        category=request.args.get("category", "SYSTEM")
    )
    return success_response(
        data=setting_response_schema.dump(setting),
        message="System setting successfully modified."
    )


@setting_bp.route("/settings/preferences", methods=["GET"])
@jwt_required()
def get_user_preferences():
    """Retrieves preference options of the current user session."""
    user_id = get_jwt_identity()
    pref = setting_service.get_user_preference(user_id)
    return success_response(
        data=pref_schema.dump(pref.preferences_json),
        message="User preferences retrieved."
    )


@setting_bp.route("/settings/preferences", methods=["PUT"])
@jwt_required()
def update_user_preferences():
    """Modifies user preferences configuration flags."""
    user_id = get_jwt_identity()
    validated_data = pref_schema.load(request.get_json())
    pref = setting_service.set_user_preference(user_id, validated_data)
    return success_response(
        data=pref_schema.dump(pref.preferences_json),
        message="User preferences updated successfully."
    )
