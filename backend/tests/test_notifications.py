import json
from app.models.user import User
from app.models.notification import Notification
from tests.test_incidents import _setup_users, _get_token

def test_notification_lifecycle(client, db, session):
    citizen, staff, officer = _setup_users(db)
    
    citizen_token = _get_token(client, "citizendev@test.com")
    staff_token = _get_token(client, "staffdev@test.com")
    
    # 1. Staff sends manual notification to citizen
    headers = {"Authorization": f"Bearer {staff_token}"}
    payload = {
        "user_id": str(citizen.id),
        "title": "Severe Weather Alert",
        "message": "Heavy rainfall warning for tomorrow.",
        "type": "IN_APP",
        "priority": "HIGH"
    }
    
    res = client.post(
        "/api/v1/notifications/send",
        data=json.dumps(payload),
        headers=headers,
        content_type="application/json"
    )
    assert res.status_code == 201
    notif_id = json.loads(res.data)["data"]["id"]
    
    # 2. Citizen lists notifications
    cit_headers = {"Authorization": f"Bearer {citizen_token}"}
    list_res = client.get(
        "/api/v1/notifications?is_read=false",
        headers=cit_headers
    )
    assert list_res.status_code == 200
    list_data = json.loads(list_res.data)
    assert list_data["pagination"]["total_records"] == 1
    assert list_data["data"][0]["title"] == "Severe Weather Alert"
    
    # 3. Citizen marks notification as read
    read_res = client.put(
        f"/api/v1/notifications/{notif_id}/read",
        headers=cit_headers
    )
    assert read_res.status_code == 200
    
    # Verify read status changed
    db_notif = db.session.query(Notification).filter_by(id=notif_id).first()
    assert db_notif.is_read is True
