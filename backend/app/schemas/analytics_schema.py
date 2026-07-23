from marshmallow import Schema, fields, validate

class PredictionRequestSchema(Schema):
    category = fields.Str(required=True, validate=validate.OneOf(["THEFT", "ASSAULT", "FIRE", "ACCIDENT", "VANDALISM", "OTHER"]))
    latitude = fields.Float(required=True, validate=validate.Range(min=-90.0, max=90.0))
    longitude = fields.Float(required=True, validate=validate.Range(min=-180.0, max=180.0))
    timestamp = fields.DateTime()


class ChartQuerySchema(Schema):
    format = fields.Str(load_default="plotly", validate=validate.OneOf(["plotly", "png"]))
