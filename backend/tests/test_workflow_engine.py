import json
from app.models.incident import Incident, Assignment
from app.models.workflow import IncidentHistory
from tests.test_incidents import _setup_users, _get_token

def test_workflow_engine_auto_assignment_and_history(client, db, session):
    citizen, staff, officer = _setup_users(db)
    
    # 1. Citizen logs an incident
    citizen_token = _get_token(client, "citizendev@test.com")
    headers = {"Authorization": f"Bearer {citizen_token}"}
    payload = {
        "title": "Water pipeline burst",
        "description": "Flooding the basement near main gate.",
        "category": "OTHER",
        "latitude": 13.0,
        "longitude": 77.5
    }
    create_res = client.post(
        "/api/v1/incidents",
        data=json.dumps(payload),
        headers=headers,
        content_type="application/json"
    )
    assert create_res.status_code == 201
    incident_id = json.loads(create_res.data)["data"]["id"]
    
    # 2. Staff auto-assigns the incident
    staff_token = _get_token(client, "staffdev@test.com")
    staff_headers = {"Authorization": f"Bearer {staff_token}"}
    
    auto_res = client.post(
        f"/api/v1/incidents/{incident_id}/auto-assign",
        headers=staff_headers
    )
    assert auto_res.status_code == 201
    assert json.loads(auto_res.data)["success"] is True
    
    # Verify assignment exists in db
    assign = db.session.query(Assignment).filter_by(incident_id=incident_id).first()
    assert assign is not None
    assert str(assign.officer_id) == str(officer.id)
    
    # Verify status transition history log was written
    hist = db.session.query(IncidentHistory).filter_by(incident_id=incident_id).all()
    # Should have SUBMITTED and ASSIGNED logs
    assert len(hist) >= 2
    assert hist[0].status_to == "SUBMITTED"
    assert hist[1].status_to == "ASSIGNED"
