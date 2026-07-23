from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from app.middleware.error_handler import AuthError

def role_required(*allowed_roles):
    """Decorator checking that the JWT claims role matches allowed system roles."""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get("role")
            
            if user_role not in allowed_roles:
                raise AuthError(
                    message="Action forbidden: Insufficient security clearances.", 
                    status_code=403, 
                    code="FORBIDDEN"
                )
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def ownership_or_admin_required(user_id_param_name="user_id"):
    """Decorator validating target user equals current user identity or possesses admin role."""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            claims = get_jwt()
            user_role = claims.get("role")
            
            # Administrators can override individual ownership locks
            if user_role == "ADMINISTRATOR":
                return fn(*args, **kwargs)
                
            target_user_id = kwargs.get(user_id_param_name)
            if target_user_id and str(target_user_id) != str(current_user_id):
                raise AuthError(
                    message="Action forbidden: You do not own this resource.",
                    status_code=403,
                    code="FORBIDDEN"
                )
            return fn(*args, **kwargs)
        return wrapper
    return decorator
