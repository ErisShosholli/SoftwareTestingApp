def test_complete_recruiter_and_candidate_api_journey(client):
    recruiter = client.post(
        "/api/auth/register",
        json={
            "name": "Riley Recruiter",
            "email": "riley@example.com",
            "password": "RecruiterPass123",
            "role": "recruiter",
        },
    ).get_json()
    candidate = client.post(
        "/api/auth/register",
        json={
            "name": "Cameron Candidate",
            "email": "cameron@example.com",
            "password": "CandidatePass123",
            "role": "candidate",
        },
    ).get_json()
    recruiter_headers = {"Authorization": f"Bearer {recruiter['token']}"}
    candidate_headers = {"Authorization": f"Bearer {candidate['token']}"}

    opportunity_response = client.post(
        "/api/opportunities",
        headers=recruiter_headers,
        json={
            "title": "Automation Engineer",
            "company": "Night Shift Tech",
            "location": "Hybrid",
            "description": "Drive API and UI quality improvements.",
            "employment_type": "Contract",
        },
    )
    assert opportunity_response.status_code == 201
    opportunity = opportunity_response.get_json()
    assert opportunity["employment_type"] == "Contract"

    application_response = client.post(
        f"/api/opportunities/{opportunity['id']}/apply",
        headers=candidate_headers,
        json={
            "applicant_name": "Cameron Candidate",
            "email": "cameron@example.com",
            "resume_text": "Python, Selenium, pytest, and Postman.",
            "cover_letter": "I can improve release confidence quickly.",
        },
    )
    assert application_response.status_code == 201
    application = application_response.get_json()

    review_response = client.put(
        f"/api/applications/{application['id']}",
        headers=recruiter_headers,
        json={"status": "accepted"},
    )
    assert review_response.status_code == 200
    assert review_response.get_json()["status"] == "accepted"

    detail_response = client.get(f"/api/opportunities/{opportunity['id']}")
    assert detail_response.status_code == 200
    assert detail_response.get_json()["application_count"] == 1


def test_candidate_can_browse_and_apply_through_web(client):
    create_response = client.post(
        "/opportunities/new",
        data={
            "title": "Automation Engineer",
            "company": "Night Shift Tech",
            "location": "Hybrid",
            "description": "Drive API and UI quality improvements.",
            "employment_type": "Internship",
        },
        follow_redirects=True,
    )
    assert create_response.status_code == 200
    assert b"Internship" in create_response.data

    homepage = client.get("/")
    assert homepage.status_code == 200
    assert b"Night Shift Tech" in homepage.data

    detail_response = client.post(
        "/opportunities/1/apply",
        data={
            "applicant_name": "Arta Candidate",
            "email": "arta@example.com",
            "resume_text": "Python, Selenium, pytest, and Postman.",
            "cover_letter": "I can improve release confidence quickly.",
        },
        follow_redirects=True,
    )
    assert detail_response.status_code == 200
    assert b"Application submitted successfully" in detail_response.data
    assert b"1 application(s) received" in detail_response.data
