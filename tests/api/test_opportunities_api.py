from career_app.extensions import db
from career_app.models import Opportunity


def test_post_opportunity_api_returns_created_resource(client):
    response = client.post(
        "/api/opportunities",
        json={
            "title": "Performance Tester",
            "company": "Vector Labs",
            "location": "Remote",
            "description": "Run load and reliability testing.",
        },
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["title"] == "Performance Tester"
    assert payload["application_count"] == 0


def test_get_opportunities_api_lists_saved_records(app, client):
    with app.app_context():
        db.session.add(
            Opportunity(
                title="Security Tester",
                company="Lockstep",
                location="Munich",
                description="Assess security quality gates.",
            )
        )
        db.session.commit()

    response = client.get("/api/opportunities")

    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload) == 1
    assert payload[0]["company"] == "Lockstep"


def test_apply_api_handles_validation_errors(app, client):
    with app.app_context():
        opportunity = Opportunity(
            title="API Tester",
            company="Core Systems",
            location="Remote",
            description="Verify backend contracts.",
        )
        db.session.add(opportunity)
        db.session.commit()
        opportunity_id = opportunity.id

    response = client.post(
        f"/api/opportunities/{opportunity_id}/apply",
        json={
            "applicant_name": "",
            "email": "candidate@example.com",
            "resume_text": "",
            "cover_letter": "",
        },
    )

    assert response.status_code == 400
    assert "Missing required fields" in response.get_json()["error"]


def test_apply_api_creates_application(client):
    client.post(
        "/api/opportunities",
        json={
            "title": "Frontend QA",
            "company": "Pixel Forge",
            "location": "Berlin",
            "description": "Validate web UX and accessibility.",
        },
    )

    response = client.post(
        "/api/opportunities/1/apply",
        json={
            "applicant_name": "Dren Candidate",
            "email": "dren@example.com",
            "resume_text": "Frontend testing with Playwright and Cypress.",
            "cover_letter": "I care about UX quality and regression safety.",
        },
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["email"] == "dren@example.com"
    assert payload["opportunity_id"] == 1


def test_delete_opportunity_api_removes_record(client):
    client.post(
        "/api/opportunities",
        json={
            "title": "Disposable Role",
            "company": "Delete API",
            "location": "Berlin",
            "description": "Used to verify deletion.",
        },
    )

    response = client.delete("/api/opportunities/1")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Opportunity deleted successfully."

    follow_up = client.get("/api/opportunities")
    assert follow_up.get_json() == []
