import json
from tests.test_incidents import _setup_users, _get_token

def test_settings_and_preferences(client, db, session):
    citizen, staff, officer = _setup_users(db)
    citizen_token = _get_token(client, "citizendev@test.com")
    
    cit_headers = {"Authorization": f"Bearer {citizen_token}"}
    
    # 1. Get default user preferences
    get_res = client.get("/api/v1/settings/preferences", headers=cit_headers)
    assert get_res.status_code == 200
    assert json.loads(get_res.data)["data"]["dark_mode"] is False
    
    # 2. Update preferences
    payload = {
        "dark_mode": True,
        "email_notifications": True,
        "sms_notifications": True,
        "in_app_notifications": False
    }
    put_res = client.put(
        "/api/v1/settings/preferences",
        data=json.dumps(payload),
        headers=cit_headers,
        content_type="application/json"
    )
    assert put_res.status_code == 200
    assert json.loads(put_res.data)["data"]["dark_mode"] is True
