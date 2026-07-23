import json
from tests.test_incidents import _setup_users, _get_token

def test_search_and_pagination(client, db, session):
    citizen, staff, officer = _setup_users(db)
    citizen_token = _get_token(client, "citizendev@test.com")
    
    headers = {"Authorization": f"Bearer {citizen_token}"}
    
    # 1. Create a dummy incident report
    payload = {
        "title": "Water leakage in pipeline",
        "description": "Main water pipeline burst near park.",
        "category": "OTHER",
        "latitude": 12.9716,
        "longitude": 77.5946
    }
    create_res = client.post(
        "/api/v1/incidents",
        data=json.dumps(payload),
        headers=headers,
        content_type="application/json"
    )
    assert create_res.status_code == 201
    
    # 2. Search for the keyword "water"
    search_res = client.get(
        "/api/v1/search/incidents?q=water&page=1&limit=10&sort_by=created_at&order=desc",
        headers=headers
    )
    assert search_res.status_code == 200
    search_data = json.loads(search_res.data)
    assert search_data["pagination"]["total_records"] == 1
    assert "water" in search_data["data"][0]["title"].lower()
