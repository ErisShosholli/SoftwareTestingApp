def test_register_login_and_read_current_user(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Robin Recruiter",
            "email": "robin@example.com",
            "password": "StrongPass123",
            "role": "recruiter",
        },
    )

    assert register_response.status_code == 201
    registered = register_response.get_json()
    assert registered["role"] == "recruiter"
    assert registered["token"]
    assert "password" not in registered

    login_response = client.post(
        "/api/auth/login",
        json={"email": "robin@example.com", "password": "StrongPass123"},
    )
    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    current_response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert current_response.status_code == 200
    assert current_response.get_json()["email"] == "robin@example.com"


def test_duplicate_registration_returns_conflict(client):
    payload = {
        "name": "Duplicate User",
        "email": "duplicate@example.com",
        "password": "StrongPass123",
        "role": "candidate",
    }
    assert client.post("/api/auth/register", json=payload).status_code == 201

    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 409
    assert "already exists" in response.get_json()["error"]


def test_invalid_login_is_rejected(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "missing@example.com", "password": "WrongPass123"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid email or password."


def test_current_user_requires_token(client):
    response = client.get("/api/users/me")

    assert response.status_code == 401
    assert "Authentication required" in response.get_json()["error"]


def test_user_can_update_and_delete_account(client, candidate_headers):
    update_response = client.put(
        "/api/users/me",
        headers=candidate_headers,
        json={"name": "Updated Candidate"},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["name"] == "Updated Candidate"

    delete_response = client.delete(
        "/api/users/me",
        headers=candidate_headers,
    )
    assert delete_response.status_code == 200

    follow_up = client.get("/api/users/me", headers=candidate_headers)
    assert follow_up.status_code == 401
