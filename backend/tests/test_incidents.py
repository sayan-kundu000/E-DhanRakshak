import json
from app.models.user import User
from app.models.incident import Incident, Assignment, RiskAssessment
from app.extensions import bcrypt

def _setup_users(db):
    """Utility helper seeding test users."""
    pw_hash = bcrypt.generate_password_hash("Password123!").decode("utf-8")
    
    citizen = User(
        email="citizendev@test.com", password_hash=pw_hash,
        full_name="Citizen Dev", role="CITIZEN", is_active=True
    )
    staff = User(
        email="staffdev@test.com", password_hash=pw_hash,
        full_name="Staff Dev", role="STAFF", is_active=True
    )
    officer = User(
        email="officerdev@test.com", password_hash=pw_hash,
        full_name="Officer Dev", role="OFFICER", is_active=True
    )
    db.session.add_all([citizen, staff, officer])
    db.session.commit()
    return citizen, staff, officer


def _get_token(client, email):
    """Utility helper to fetch JWT access token."""
    login_payload = {"email": email, "password": "Password123!"}
    res = client.post("/api/v1/auth/login", data=json.dumps(login_payload), content_type="application/json")
    return json.loads(res.data)["data"]["access_token"]


def test_incident_creation_and_risk_scoring(client, db, session):
    """Verifies that citizen reports trigger scoring calculations and audits logging."""
    citizen, staff, officer = _setup_users(db)
    citizen_token = _get_token(client, "citizendev@test.com")
    
    payload = {
        "title": "Robbery at Central Store",
        "description": "Armed robbery at main street corner.",
        "category": "THEFT",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    
    headers = {"Authorization": f"Bearer {citizen_token}"}
    
    from unittest.mock import patch
    import datetime as dt
    mock_now = dt.datetime(2026, 7, 23, 12, 0, 0, tzinfo=dt.timezone.utc)
    
    with patch("app.services.incident_service.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_now
        mock_datetime.timezone = dt.timezone
        mock_datetime.timedelta = dt.timedelta
        
        response = client.post(
            "/api/v1/incidents",
            data=json.dumps(payload),
            headers=headers,
            content_type="application/json"
        )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["data"]["status"] == "SUBMITTED"
    
    incident_id = data["data"]["id"]
    
    # Query database to confirm RiskAssessment was created with the mathematical algorithm
    assessment = db.session.query(RiskAssessment).filter_by(incident_id=incident_id).first()
    assert assessment is not None
    # THEFT weight=5 (S*6 = 30), no spatial history (D=0), day shift temporal (T=4 * 0.5 = 2). Total = 32
    assert float(assessment.risk_score) == 32.0
    assert assessment.factors["severity_weight"] == 5.0


def test_incident_assignment_and_officer_lifecycle(client, db, session):
    """Verifies assignment state shifts as dispatcher maps officer and officer resolves."""
    citizen, staff, officer = _setup_users(db)
    
    # 1. Citizen logs incident
    citizen_token = _get_token(client, "citizendev@test.com")
    headers = {"Authorization": f"Bearer {citizen_token}"}
    payload = {
        "title": "Building Fire Outbreak", "description": "Smokes from third floor.",
        "category": "FIRE", "latitude": 34.0522, "longitude": -118.2437
    }
    create_res = client.post("/api/v1/incidents", data=json.dumps(payload), headers=headers, content_type="application/json")
    incident_id = json.loads(create_res.data)["data"]["id"]
    
    # 2. Staff maps incident to Officer
    staff_token = _get_token(client, "staffdev@test.com")
    staff_headers = {"Authorization": f"Bearer {staff_token}"}
    assign_payload = {
        "incident_id": incident_id,
        "officer_id": str(officer.id)
    }
    assign_res = client.post(
        "/api/v1/assignments",
        data=json.dumps(assign_payload),
        headers=staff_headers,
        content_type="application/json"
    )
    assert assign_res.status_code == 201
    assignment_id = json.loads(assign_res.data)["data"]["id"]
    
    # Verify incident state changed to ASSIGNED
    incident_state = db.session.query(Incident).filter_by(id=incident_id).first()
    assert incident_state.status == "ASSIGNED"
    
    # 3. Officer ACCEPTS assignment
    officer_token = _get_token(client, "officerdev@test.com")
    officer_headers = {"Authorization": f"Bearer {officer_token}"}
    status_payload = {"status": "ACCEPTED"}
    accept_res = client.put(
        f"/api/v1/assignments/{assignment_id}/status",
        data=json.dumps(status_payload),
        headers=officer_headers,
        content_type="application/json"
    )
    assert accept_res.status_code == 200
    
    # Verify incident state changed to IN_PROGRESS
    incident_state = db.session.query(Incident).filter_by(id=incident_id).first()
    assert incident_state.status == "IN_PROGRESS"
    
    # 4. Officer RESOLVES assignment
    status_payload_resolve = {"status": "RESOLVED"}
    resolve_res = client.put(
        f"/api/v1/assignments/{assignment_id}/status",
        data=json.dumps(status_payload_resolve),
        headers=officer_headers,
        content_type="application/json"
    )
    assert resolve_res.status_code == 200
    
    # Verify incident state changed to RESOLVED
    incident_state = db.session.query(Incident).filter_by(id=incident_id).first()
    assert incident_state.status == "RESOLVED"
