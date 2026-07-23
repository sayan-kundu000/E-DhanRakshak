import re
from marshmallow import Schema, fields, validate, validates, ValidationError

# Allowed role enum matching the database constraint
ALLOWED_ROLES = ["ADMINISTRATOR", "OFFICER", "STAFF", "CITIZEN", "GUEST"]

def validate_password_complexity(value: str):
    """Enforces strict password complexity requirements."""
    if len(value) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", value):
        raise ValidationError("Password must contain at least one uppercase character.")
    if not re.search(r"[a-z]", value):
        raise ValidationError("Password must contain at least one lowercase character.")
    if not re.search(r"\d", value):
        raise ValidationError("Password must contain at least one number.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
        raise ValidationError("Password must contain at least one special character.")


class RegisterSchema(Schema):
    """Validates parameters sent during signup requests."""
    email = fields.Email(required=True, validate=validate.Length(max=150))
    password = fields.Str(required=True, validate=validate_password_complexity)
    full_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    role = fields.Str(required=True, validate=validate.OneOf(ALLOWED_ROLES))


class LoginSchema(Schema):
    """Validates login credentials."""
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class ProfileUpdateSchema(Schema):
    """Validates updates to a user's personal details."""
    full_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))


class ChangePasswordSchema(Schema):
    """Validates request parameters to change account password."""
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate_password_complexity)


class UserResponseSchema(Schema):
    """Serializes user record profiles to standard JSON payloads."""
    id = fields.UUID(dump_only=True)
    email = fields.Email(dump_only=True)
    full_name = fields.Str(dump_only=True)
    role = fields.Str(dump_only=True)
    is_active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
