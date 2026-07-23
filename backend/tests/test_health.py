import json

def test_simple_health_check(client):
    """Verifies that the /api/v1/health endpoint runs and returns a 200 success response."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data["success"] is True
    assert "E-DhanRakshak API server is running" in data["message"]


def test_detailed_health_check_sqlite_fallback(client, app):
    """Verifies detailed health checks run successfully with sqlite parameters."""
    response = client.get("/api/v1/health/details")
    # Note: Can return 200 or 503 depending on Redis server connectivity during test runs
    assert response.status_code in [200, 503]
    
    data = json.loads(response.data)
    assert "data" in data
    assert "database" in data["data"]
    assert "redis" in data["data"]
    assert "storage" in data["data"]
