from career_app.extensions import db
from career_app.models import Application, Opportunity


def test_create_opportunity_route_saves_new_model_field(app, client):
    response = client.post(
        "/opportunities/new",
        data={
            "title": "Test Analyst",
            "company": "Blue Corp",
            "location": "Berlin",
            "description": "Support exploratory and automated testing.",
            "employment_type": "Part-time",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Opportunity posted successfully" in response.data
    assert b"Part-time" in response.data

    with app.app_context():
        saved = Opportunity.query.filter_by(company="Blue Corp").first()
        assert saved is not None
        assert saved.employment_type == "Part-time"


def test_apply_route_creates_related_application_record(app, client):
    with app.app_context():
        opportunity = Opportunity(
            title="QA Lead",
            company="Signal House",
            location="Remote",
            description="Lead the test strategy.",
            employment_type="Full-time",
        )
        db.session.add(opportunity)
        db.session.commit()
        opportunity_id = opportunity.id

    response = client.post(
        f"/opportunities/{opportunity_id}/apply",
        data={
            "applicant_name": "Sara Dev",
            "email": "sara@example.com",
            "resume_text": "Experienced with CI and API testing.",
            "cover_letter": "I build resilient test suites.",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Application submitted successfully" in response.data

    with app.app_context():
        application = Application.query.filter_by(email="sara@example.com").first()
        assert application.opportunity_id == opportunity_id
        assert application.status == "submitted"


def test_create_opportunity_route_shows_validation_errors(client):
    response = client.post(
        "/opportunities/new",
        data={"title": "", "company": "", "location": "", "description": ""},
    )

    assert response.status_code == 400
    assert b"Missing required fields" in response.data


def test_delete_opportunity_route_removes_record(app, client):
    with app.app_context():
        opportunity = Opportunity(
            title="Remove Listing",
            company="Blue Corp",
            location="Berlin",
            description="Short-lived role.",
        )
        db.session.add(opportunity)
        db.session.commit()
        opportunity_id = opportunity.id

    response = client.post(
        f"/opportunities/{opportunity_id}/delete",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Opportunity deleted successfully" in response.data

    with app.app_context():
        assert db.session.get(Opportunity, opportunity_id) is None
