def test_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_opportunity_create_requires_authentication(client, opportunity_payload):
    response = client.post("/api/opportunities", json=opportunity_payload)

    assert response.status_code == 401


def test_opportunity_crud_includes_modified_field(
    client,
    recruiter_headers,
    opportunity_payload,
):
    create_response = client.post(
        "/api/opportunities",
        headers=recruiter_headers,
        json=opportunity_payload,
    )
    assert create_response.status_code == 201
    created = create_response.get_json()
    assert created["employment_type"] == "Full-time"
    opportunity_id = created["id"]

    list_response = client.get("/api/opportunities")
    assert list_response.status_code == 200
    assert list_response.get_json()[0]["id"] == opportunity_id

    get_response = client.get(f"/api/opportunities/{opportunity_id}")
    assert get_response.status_code == 200
    assert get_response.get_json()["company"] == "Vector Labs"

    update_response = client.put(
        f"/api/opportunities/{opportunity_id}",
        headers=recruiter_headers,
        json={"employment_type": "Contract", "status": "closed"},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["employment_type"] == "Contract"
    assert update_response.get_json()["status"] == "closed"

    delete_response = client.delete(
        f"/api/opportunities/{opportunity_id}",
        headers=recruiter_headers,
    )
    assert delete_response.status_code == 200
    assert client.get(f"/api/opportunities/{opportunity_id}").status_code == 404


def test_opportunity_update_and_delete_require_auth(
    client,
    recruiter_headers,
    opportunity_payload,
):
    created = client.post(
        "/api/opportunities",
        headers=recruiter_headers,
        json=opportunity_payload,
    ).get_json()

    assert client.put(
        f"/api/opportunities/{created['id']}",
        json={"status": "closed"},
    ).status_code == 401
    assert client.delete(
        f"/api/opportunities/{created['id']}"
    ).status_code == 401


def test_opportunity_validation_rejects_bad_modified_field(
    client,
    recruiter_headers,
    opportunity_payload,
):
    opportunity_payload["employment_type"] = "Freelance"

    response = client.post(
        "/api/opportunities",
        headers=recruiter_headers,
        json=opportunity_payload,
    )

    assert response.status_code == 400
    assert "employment_type" in response.get_json()["error"]
