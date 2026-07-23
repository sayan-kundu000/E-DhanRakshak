from marshmallow import Schema, fields, validate

class SearchQuerySchema(Schema):
    q = fields.Str(validate=validate.Length(max=100))
    status = fields.Str(validate=validate.Length(max=30))
    category = fields.Str(validate=validate.Length(max=50))
    reporter_id = fields.UUID()
    officer_id = fields.UUID()
    start_date = fields.DateTime()
    end_date = fields.DateTime()
    
    # pagination and sorting
    page = fields.Int(validate=validate.Range(min=1), load_default=1)
    limit = fields.Int(validate=validate.Range(min=1, max=100), load_default=10)
    sort_by = fields.Str(validate=validate.OneOf(["created_at", "title", "status", "category"]), load_default="created_at")
    order = fields.Str(validate=validate.OneOf(["asc", "desc"]), load_default="desc")
