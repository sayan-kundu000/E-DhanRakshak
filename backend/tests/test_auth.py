import json
from app.models.user import User
from app.extensions import bcrypt

def test_user_registration_success(client, db, session):
    """Verifies that a user can register successfully with valid parameters."""
    payload = {
        "email": "citizen@test.com",
        "password": "Password123!",
        "full_name": "Test Citizen",
        "role": "CITIZEN"
    }
    
    response = client.post(
        "/api/v1/auth/register",
        data=json.dumps(payload),
        content_type="application/json"
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["data"]["email"] == "citizen@test.com"
    assert data["data"]["role"] == "CITIZEN"


def test_registration_complexity_failure(client):
    """Verifies that the registration fails when password lacks complexity."""
    payload = {
        "email": "invalidpw@test.com",
        "password": "simple",
        "full_name": "Simple User",
        "role": "CITIZEN"
    }
    
    response = client.post(
        "/api/v1/auth/register",
        data=json.dumps(payload),
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False
    assert "password" in data["error"]["details"]


def test_user_login_and_refresh_cycle(client, db, session):
    """Verifies successful login processes and JWT token refresh capability."""
    # Seed user record manually into test db session
    pw_hash = bcrypt.generate_password_hash("Secure123!").decode("utf-8")
    user = User(
        email="officer@test.com",
        password_hash=pw_hash,
        full_name="Officer Test",
        role="OFFICER",
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    
    # 1. Test Login
    login_payload = {
        "email": "officer@test.com",
        "password": "Secure123!"
    }
    response = client.post(
        "/api/v1/auth/login",
        data=json.dumps(login_payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    
    tokens = json.loads(response.data)["data"]
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    
    # 2. Test Refresh Token
    refresh_headers = {
        "Authorization": f"Bearer {tokens['refresh_token']}"
    }
    refresh_response = client.post(
        "/api/v1/auth/refresh",
        headers=refresh_headers
    )
    assert refresh_response.status_code == 200
    refresh_data = json.loads(refresh_response.data)["data"]
    assert "access_token" in refresh_data


def test_role_authorization_restriction(client, db, session):
    """Verifies that non-admin accounts cannot access user activation routes."""
    # Seed two users: Citizen and Admin
    admin_hash = bcrypt.generate_password_hash("Admin123!").decode("utf-8")
    admin_user = User(
        email="admin@test.com", password_hash=admin_hash,
        full_name="System Admin", role="ADMINISTRATOR", is_active=True
    )
    
    citizen_hash = bcrypt.generate_password_hash("Citizen123!").decode("utf-8")
    citizen_user = User(
        email="target@test.com", password_hash=citizen_hash,
        full_name="Target Citizen", role="CITIZEN", is_active=True
    )
    
    db.session.add(admin_user)
    db.session.add(citizen_user)
    db.session.commit()
    
    # Get token for citizen and attempt deactivation
    login_payload = {"email": "target@test.com", "password": "Citizen123!"}
    login_res = client.post("/api/v1/auth/login", data=json.dumps(login_payload), content_type="application/json")
    citizen_token = json.loads(login_res.data)["data"]["access_token"]
    
    # PUT request to change target's activation state using citizen's token (should be forbidden)
    headers = {"Authorization": f"Bearer {citizen_token}"}
    toggle_res = client.put(
        f"/api/v1/auth/users/{citizen_user.id}/activation",
        data=json.dumps({"is_active": False}),
        headers=headers,
        content_type="application/json"
    )
    assert toggle_res.status_code == 403
    
    # Put request using admin's token (should succeed)
    admin_login = {"email": "admin@test.com", "password": "Admin123!"}
    admin_login_res = client.post("/api/v1/auth/login", data=json.dumps(admin_login), content_type="application/json")
    admin_token = json.loads(admin_login_res.data)["data"]["access_token"]
    
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    toggle_res_admin = client.put(
        f"/api/v1/auth/users/{citizen_user.id}/activation",
        data=json.dumps({"is_active": False}),
        headers=admin_headers,
        content_type="application/json"
    )
    assert toggle_res_admin.status_code == 200
    
    # Query database state to confirm target citizen status changed
    updated_citizen = db.session.query(User).filter_by(email="target@test.com").first()
    assert updated_citizen.is_active is False
