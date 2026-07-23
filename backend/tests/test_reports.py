import json
from tests.test_incidents import _setup_users, _get_token

def test_report_generation(client, db, session):
    citizen, staff, officer = _setup_users(db)
    staff_token = _get_token(client, "staffdev@test.com")
    
    headers = {"Authorization": f"Bearer {staff_token}"}
    
    # 1. Get Summary statistics
    res = client.get(
        "/api/v1/reports/summary?interval=weekly",
        headers=headers
    )
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["success"] is True
    assert "total_incidents" in data["data"]
    
    # 2. Export CSV reports
    csv_res = client.get(
        "/api/v1/reports/export?interval=weekly&format=csv",
        headers=headers
    )
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.mimetype
