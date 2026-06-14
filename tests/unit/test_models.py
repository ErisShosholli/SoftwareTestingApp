from career_app.models import Application, Opportunity, User


def test_user_password_is_hashed_and_checkable():
    user = User(
        name="Model User",
        email="model@example.com",
        role="candidate",
        api_token="temporary",
    )
    user.set_password("StrongPass123")

    assert user.password_hash != "StrongPass123"
    assert user.check_password("StrongPass123")
    assert not user.check_password("wrong-password")


def test_user_token_rotation_returns_new_token():
    user = User(api_token="old-token")

    token = user.rotate_token()

    assert token == user.api_token
    assert token != "old-token"
    assert len(token) >= 32


def test_modified_opportunity_model_has_employment_type(app):
    with app.app_context():
        opportunity = Opportunity(
            title="Model Test",
            company="CareerFlow",
            location="Remote",
            description="Verify the modified model field.",
            employment_type="Contract",
        )

        assert opportunity.employment_type == "Contract"


def test_application_relationship_links_to_opportunity(app):
    with app.app_context():
        opportunity = Opportunity(
            title="Relationship Test",
            company="CareerFlow",
            location="Remote",
            description="Verify model relationships.",
        )
        application = Application(
            applicant_name="Relational Candidate",
            email="relation@example.com",
            resume_text="Testing experience.",
            cover_letter="Ready to contribute.",
            opportunity=opportunity,
        )

        assert application.opportunity is opportunity
        assert application in opportunity.applications
