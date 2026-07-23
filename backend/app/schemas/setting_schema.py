from marshmallow import Schema, fields, validate

class SystemSettingResponseSchema(Schema):
    id = fields.UUID(dump_only=True)
    key = fields.Str(dump_only=True)
    value = fields.Str(dump_only=True)
    description = fields.Str(dump_only=True)
    category = fields.Str(dump_only=True)


class SystemSettingUpdateSchema(Schema):
    value = fields.Str(required=True, validate=validate.Length(min=1))
    description = fields.Str(validate=validate.Length(max=500))


class UserPreferenceSchema(Schema):
    dark_mode = fields.Bool(load_default=False)
    email_notifications = fields.Bool(load_default=True)
    sms_notifications = fields.Bool(load_default=False)
    in_app_notifications = fields.Bool(load_default=True)
