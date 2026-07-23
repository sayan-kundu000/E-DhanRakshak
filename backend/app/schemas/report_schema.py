from marshmallow import Schema, fields, validate

class ReportRequestSchema(Schema):
    interval = fields.Str(required=True, validate=validate.OneOf(["daily", "weekly", "monthly", "yearly"]))
    format = fields.Str(load_default="csv", validate=validate.OneOf(["csv", "pdf", "json"]))


class ReportResponseSchema(Schema):
    interval = fields.Str(dump_only=True)
    start_date = fields.Str(dump_only=True)
    total_incidents = fields.Int(dump_only=True)
    average_risk_score = fields.Float(dump_only=True)
    by_category = fields.Dict(keys=fields.Str(), values=fields.Int(), dump_only=True)
    by_status = fields.Dict(keys=fields.Str(), values=fields.Int(), dump_only=True)
