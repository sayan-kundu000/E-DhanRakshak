from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.notification_service import NotificationService
from app.schemas.notification_schema import NotificationResponseSchema, NotificationSendSchema
from app.utils.helpers import success_response, paginated_response
from app.middleware.auth_middleware import role_required

notification_bp = Blueprint("notification", __name__, url_prefix="/api/v1")
notification_service = NotificationService()

response_schema = NotificationResponseSchema()
send_schema = NotificationSendSchema()

@notification_bp.route("/notifications", methods=["GET"])
@jwt_required()
def list_notifications():
    """Lists notifications for the current authenticated user."""
    user_id = get_jwt_identity()
    is_read = request.args.get("is_read")
    if is_read is not None:
        is_read = is_read.lower() == "true"
        
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    records, total = notification_service.list_notifications(user_id, is_read, page, limit)
    serialized = response_schema.dump(records, many=True)
    return paginated_response(
        data=serialized,
        total_records=total,
        page=page,
        limit=limit,
        message="Notifications retrieved successfully."
    )


@notification_bp.route("/notifications/<uuid:notification_id>/read", methods=["PUT"])
@jwt_required()
def mark_notification_read(notification_id):
    """Marks a specific notification as read."""
    user_id = get_jwt_identity()
    notification = notification_service.mark_as_read(str(notification_id), user_id)
    return success_response(
        data=response_schema.dump(notification),
        message="Notification marked as read."
    )


@notification_bp.route("/notifications/read-all", methods=["PUT"])
@jwt_required()
def mark_all_notifications_read():
    """Marks all notifications for current user as read."""
    user_id = get_jwt_identity()
    count = notification_service.mark_all_read(user_id)
    return success_response(
        data={"updated_count": count},
        message="All notifications marked as read."
    )


@notification_bp.route("/notifications/send", methods=["POST"])
@role_required("ADMINISTRATOR", "STAFF")
def send_manual_notification():
    """Enables dispatchers/admins to send custom manual alert notifications."""
    validated_data = send_schema.load(request.get_json())
    new_notif = notification_service.send_notification(
        user_id=str(validated_data["user_id"]),
        title=validated_data["title"],
        message=validated_data["message"],
        notification_type=validated_data.get("type", "IN_APP"),
        priority=validated_data.get("priority", "MEDIUM")
    )
    return success_response(
        data=response_schema.dump(new_notif),
        message="Manual notification sent.",
        status_code=201
    )
