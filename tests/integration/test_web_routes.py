from career_app.models import Application, Opportunity


def test_create_opportunity_route_saves_to_database(app, client):
    response = client.post(
        "/opportunities/new",
        data={
            "title": "Test Analyst",
            "company": "Blue Corp",
            "location": "Berlin",
            "description": "Support exploratory and automated testing.",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Opportunity posted successfully" in response.data

    with app.app_context():
        saved = Opportunity.query.filter_by(company="Blue Corp").first()
        assert saved is not None


def test_apply_route_creates_application_record(app, client):
    with app.app_context():
        opportunity = Opportunity(
            title="QA Lead",
            company="Signal House",
            location="Remote",
            description="Lead the test strategy.",
        )
        from career_app.extensions import db

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
        assert application is not None
        assert application.opportunity_id == opportunity_id


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
        from career_app.extensions import db

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
        assert Opportunity.query.get(opportunity_id) is None
