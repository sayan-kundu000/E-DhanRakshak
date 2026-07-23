from marshmallow import Schema, fields, validate, validates, ValidationError

# Allowed category enum matching target rules
ALLOWED_CATEGORIES = ["THEFT", "ASSAULT", "FIRE", "ACCIDENT", "VANDALISM", "OTHER"]
ALLOWED_STATUSES = ["DRAFT", "SUBMITTED", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "CLOSED"]
ALLOWED_ASSIGNMENT_STATUSES = ["ASSIGNED", "ACCEPTED", "REJECTED", "RESOLVED"]


class RiskAssessmentSchema(Schema):
    """Serializes statistical scoring calculations."""
    risk_score = fields.Float(dump_only=True)
    factors = fields.Dict(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class AssignmentResponseSchema(Schema):
    """Serializes dispatcher routing outputs."""
    id = fields.UUID(dump_only=True)
    incident_id = fields.UUID(dump_only=True)
    officer_id = fields.UUID(dump_only=True)
    assigned_by = fields.UUID(dump_only=True)
    status = fields.Str(dump_only=True)
    rejection_reason = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class IncidentCreateSchema(Schema):
    """Validates inputs for logging new reports."""
    title = fields.Str(required=True, validate=validate.Length(min=5, max=150))
    description = fields.Str(required=True)
    category = fields.Str(required=True, validate=validate.OneOf(ALLOWED_CATEGORIES))
    latitude = fields.Float(required=True, validate=validate.Range(min=-90.0, max=90.0))
    longitude = fields.Float(required=True, validate=validate.Range(min=-180.0, max=180.0))


class IncidentUpdateSchema(Schema):
    """Validates parameters modifying details."""
    title = fields.Str(validate=validate.Length(min=5, max=150))
    description = fields.Str()
    category = fields.Str(validate=validate.OneOf(ALLOWED_CATEGORIES))
    latitude = fields.Float(validate=validate.Range(min=-90.0, max=90.0))
    longitude = fields.Float(validate=validate.Range(min=-180.0, max=180.0))


class IncidentResponseSchema(Schema):
    """Standardizes JSON output representation for incident details."""
    id = fields.UUID(dump_only=True)
    reporter_id = fields.UUID(dump_only=True)
    title = fields.Str(dump_only=True)
    description = fields.Str(dump_only=True)
    category = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    latitude = fields.Float(dump_only=True)
    longitude = fields.Float(dump_only=True)
    attachment_url = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Nested relations representation
    risk_assessment = fields.Nested(RiskAssessmentSchema, dump_only=True)
    assignment = fields.Nested(AssignmentResponseSchema, dump_only=True)


class AssignmentCreateSchema(Schema):
    """Validates input payload when dispatchers assign incidents to officers."""
    incident_id = fields.UUID(required=True)
    officer_id = fields.UUID(required=True)


class AssignmentUpdateSchema(Schema):
    """Validates state updates submitted by officers."""
    status = fields.Str(required=True, validate=validate.OneOf(ALLOWED_ASSIGNMENT_STATUSES))
    rejection_reason = fields.Str(validate=validate.Length(max=500))

    @validates("status")
    def validate_status_transitions(self, value, **kwargs):
        if value == "ASSIGNED":
            raise ValidationError("Cannot manually reset assignment status back to ASSIGNED.")
