import json
from tests.test_incidents import _setup_users, _get_token

def test_analytics_and_predictions(client, db, session):
    citizen, staff, officer = _setup_users(db)
    citizen_token = _get_token(client, "citizendev@test.com")
    staff_token = _get_token(client, "staffdev@test.com")

    # 1. Test Prediction (with rule-based fallback check)
    headers = {"Authorization": f"Bearer {citizen_token}"}
    pred_res = client.get(
        "/api/v1/analytics/prediction?category=FIRE&latitude=12.9716&longitude=77.5946",
        headers=headers
    )
    assert pred_res.status_code == 200
    pred_data = json.loads(pred_res.data)
    assert pred_data["success"] is True
    assert pred_data["data"]["priority"] == "HIGH"
    assert pred_data["data"]["method"] == "RULES_ENGINE"

    # 2. Test Trends query
    trends_res = client.get(
        "/api/v1/analytics/trends",
        headers=headers
    )
    assert trends_res.status_code == 200
    trends_data = json.loads(trends_res.data)
    assert trends_data["success"] is True
    assert "growth_rate_percent" in trends_data["data"]

    # 3. Test Dashboard (Citizen context)
    dash_res = client.get(
        "/api/v1/analytics/dashboard",
        headers=headers
    )
    assert dash_res.status_code == 200
    dash_data = json.loads(dash_res.data)
    assert dash_data["data"]["role"] == "CITIZEN"

    # 4. Test Dashboard (Admin/Staff context)
    adm_headers = {"Authorization": f"Bearer {staff_token}"}
    adm_dash_res = client.get(
        "/api/v1/analytics/dashboard",
        headers=adm_headers
    )
    assert adm_dash_res.status_code == 200
    adm_dash_data = json.loads(adm_dash_res.data)
    assert adm_dash_data["data"]["role"] == "ADMINISTRATOR"

    # 5. Test Charts (Plotly JSON format)
    chart_res = client.get(
        "/api/v1/analytics/charts/category?format=plotly",
        headers=headers
    )
    assert chart_res.status_code == 200
    chart_data = json.loads(chart_res.data)
    assert chart_data["success"] is True

    # 6. Test Charts (Matplotlib PNG image stream format)
    png_res = client.get(
        "/api/v1/analytics/charts/category?format=png",
        headers=headers
    )
    assert png_res.status_code == 200
    assert png_res.mimetype == "image/png"
