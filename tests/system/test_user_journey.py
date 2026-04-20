def test_candidate_can_browse_and_apply_for_opportunity(client):
    create_response = client.post(
        "/opportunities/new",
        data={
            "title": "Automation Engineer",
            "company": "Night Shift Tech",
            "location": "Hybrid",
            "description": "Drive API and UI quality improvements.",
        },
        follow_redirects=True,
    )
    assert create_response.status_code == 200
    assert b"Automation Engineer" in create_response.data

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


def test_recruiter_can_delete_an_opportunity(client):
    client.post(
        "/opportunities/new",
        data={
            "title": "Contract QA",
            "company": "Delete Flow",
            "location": "Remote",
            "description": "Temporary engagement.",
        },
        follow_redirects=True,
    )

    delete_response = client.post("/opportunities/1/delete", follow_redirects=True)
    assert delete_response.status_code == 200
    assert b"Opportunity deleted successfully" in delete_response.data

    homepage = client.get("/")
    assert b"Delete Flow" not in homepage.data
