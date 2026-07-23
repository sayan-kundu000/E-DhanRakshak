from marshmallow import Schema, fields

class FileAttachmentResponseSchema(Schema):
    id = fields.UUID(dump_only=True)
    original_name = fields.Str(dump_only=True)
    stored_name = fields.Str(dump_only=True)
    extension = fields.Str(dump_only=True)
    content_type = fields.Str(dump_only=True)
    file_size = fields.Int(dump_only=True)
    owner_id = fields.UUID(dump_only=True)
    checksum = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
