def create_opportunity(client, headers, payload):
    response = client.post(
        "/api/opportunities",
        headers=headers,
        json=payload,
    )
    assert response.status_code == 201
    return response.get_json()


def test_application_crud_workflow(
    client,
    recruiter_headers,
    candidate_headers,
    opportunity_payload,
    application_payload,
):
    opportunity = create_opportunity(
        client,
        recruiter_headers,
        opportunity_payload,
    )
    opportunity_id = opportunity["id"]

    create_response = client.post(
        f"/api/opportunities/{opportunity_id}/applications",
        headers=candidate_headers,
        json=application_payload,
    )
    assert create_response.status_code == 201
    created = create_response.get_json()
    assert created["status"] == "submitted"
    application_id = created["id"]

    list_response = client.get(
        "/api/applications",
        headers=recruiter_headers,
    )
    assert list_response.status_code == 200
    assert list_response.get_json()[0]["id"] == application_id

    opportunity_apps = client.get(
        f"/api/opportunities/{opportunity_id}/applications",
        headers=recruiter_headers,
    )
    assert opportunity_apps.status_code == 200
    assert len(opportunity_apps.get_json()) == 1

    get_response = client.get(
        f"/api/applications/{application_id}",
        headers=candidate_headers,
    )
    assert get_response.status_code == 200
    assert get_response.get_json()["email"] == "casey@example.com"

    update_response = client.put(
        f"/api/applications/{application_id}",
        headers=recruiter_headers,
        json={"status": "reviewing"},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["status"] == "reviewing"

    delete_response = client.delete(
        f"/api/applications/{application_id}",
        headers=recruiter_headers,
    )
    assert delete_response.status_code == 200
    assert client.get(
        f"/api/applications/{application_id}",
        headers=recruiter_headers,
    ).status_code == 404


def test_application_mutations_require_authentication(
    client,
    recruiter_headers,
    opportunity_payload,
    application_payload,
):
    opportunity = create_opportunity(
        client,
        recruiter_headers,
        opportunity_payload,
    )

    response = client.post(
        f"/api/opportunities/{opportunity['id']}/apply",
        json=application_payload,
    )

    assert response.status_code == 401


def test_duplicate_application_returns_conflict(
    client,
    recruiter_headers,
    candidate_headers,
    opportunity_payload,
    application_payload,
):
    opportunity = create_opportunity(
        client,
        recruiter_headers,
        opportunity_payload,
    )
    url = f"/api/opportunities/{opportunity['id']}/apply"
    assert client.post(
        url,
        headers=candidate_headers,
        json=application_payload,
    ).status_code == 201

    response = client.post(
        url,
        headers=candidate_headers,
        json=application_payload,
    )

    assert response.status_code == 409
    assert "already applied" in response.get_json()["error"]


def test_closed_opportunity_rejects_application(
    client,
    recruiter_headers,
    candidate_headers,
    opportunity_payload,
    application_payload,
):
    opportunity_payload["status"] = "closed"
    opportunity = create_opportunity(
        client,
        recruiter_headers,
        opportunity_payload,
    )

    response = client.post(
        f"/api/opportunities/{opportunity['id']}/apply",
        headers=candidate_headers,
        json=application_payload,
    )

    assert response.status_code == 400
    assert "closed" in response.get_json()["error"]
