from marshmallow import Schema, fields, validate

class NotificationResponseSchema(Schema):
    id = fields.UUID(dump_only=True)
    user_id = fields.UUID(dump_only=True)
    title = fields.Str(dump_only=True)
    message = fields.Str(dump_only=True)
    type = fields.Str(dump_only=True)
    priority = fields.Str(dump_only=True)
    is_read = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class NotificationSendSchema(Schema):
    user_id = fields.UUID(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=3, max=150))
    message = fields.Str(required=True, validate=validate.Length(min=5))
    type = fields.Str(validate=validate.OneOf(["IN_APP", "EMAIL", "SMS"]), load_default="IN_APP")
    priority = fields.Str(validate=validate.OneOf(["LOW", "MEDIUM", "HIGH"]), load_default="MEDIUM")
