from unittest.mock import Mock, patch

import pytest

from career_app.extensions import db
from career_app.models import Application, Opportunity
from career_app.services import (
    ConflictError,
    ValidationError,
    create_opportunity,
    delete_opportunity,
    serialize_opportunity,
    submit_application,
    update_application,
    update_opportunity,
)


def test_create_opportunity_persists_modified_field_and_notifies(app):
    notifier = Mock()

    with app.app_context():
        opportunity = create_opportunity(
            {
                "title": "QA Engineer",
                "company": "Dracula Labs",
                "location": "Remote",
                "description": "Own testing strategy.",
                "employment_type": "Contract",
            },
            notifier=notifier,
        )

        saved = db.session.get(Opportunity, opportunity.id)
        assert saved.employment_type == "Contract"
        assert serialize_opportunity(saved)["employment_type"] == "Contract"
        notifier.assert_called_once_with("New opportunity created", "Dracula Labs")


def test_create_opportunity_rejects_invalid_employment_type(app):
    with app.app_context():
        with pytest.raises(ValidationError, match="employment_type"):
            create_opportunity(
                {
                    "title": "QA Engineer",
                    "company": "Acme",
                    "location": "Remote",
                    "description": "Test products.",
                    "employment_type": "Freelance",
                },
                notifier=Mock(),
            )


def test_update_opportunity_changes_status_and_employment_type(app):
    with app.app_context():
        opportunity = create_opportunity(
            {
                "title": "SDET",
                "company": "North Wind",
                "location": "Remote",
                "description": "Test pipelines.",
            },
            notifier=Mock(),
        )

        updated = update_opportunity(
            opportunity.id,
            {"status": "closed", "employment_type": "Part-time"},
        )

        assert updated.status == "closed"
        assert updated.employment_type == "Part-time"


def test_submit_application_uses_notification_patch(app):
    with app.app_context():
        opportunity = create_opportunity(
            {
                "title": "Backend Developer",
                "company": "Acme",
                "location": "Prishtina",
                "description": "Build APIs.",
            },
            notifier=Mock(),
        )

        with patch("career_app.services.send_notification") as notification:
            application = submit_application(
                opportunity.id,
                {
                    "applicant_name": "Lina Test",
                    "email": "lina@example.com",
                    "resume_text": "3 years in Python.",
                    "cover_letter": "I enjoy reliable systems.",
                },
                notifier=notification,
            )

            assert application.status == "submitted"
            notification.assert_called_once_with(
                "New application submitted",
                "lina@example.com",
            )


def test_submit_application_rejects_closed_opportunity(app):
    with app.app_context():
        opportunity = create_opportunity(
            {
                "title": "SDET",
                "company": "North Wind",
                "location": "Remote",
                "description": "Test pipelines.",
                "status": "closed",
            },
            notifier=Mock(),
        )

        with pytest.raises(ValidationError, match="Applications are closed"):
            submit_application(
                opportunity.id,
                {
                    "applicant_name": "Mira",
                    "email": "mira@example.com",
                    "resume_text": "Automation and API work.",
                    "cover_letter": "Ready to contribute.",
                },
                notifier=Mock(),
            )


def test_duplicate_application_is_rejected(app):
    payload = {
        "applicant_name": "Mira",
        "email": "mira@example.com",
        "resume_text": "Automation and API work.",
        "cover_letter": "Ready to contribute.",
    }
    with app.app_context():
        opportunity = create_opportunity(
            {
                "title": "SDET",
                "company": "North Wind",
                "location": "Remote",
                "description": "Test pipelines.",
            },
            notifier=Mock(),
        )
        submit_application(opportunity.id, payload, notifier=Mock())

        with pytest.raises(ConflictError, match="already applied"):
            submit_application(opportunity.id, payload, notifier=Mock())


def test_update_application_changes_review_status(app):
    with app.app_context():
        opportunity = create_opportunity(
            {
                "title": "Tester",
                "company": "Status Corp",
                "location": "Remote",
                "description": "Review application statuses.",
            },
            notifier=Mock(),
        )
        application = submit_application(
            opportunity.id,
            {
                "applicant_name": "Review Candidate",
                "email": "review@example.com",
                "resume_text": "Quality engineering.",
                "cover_letter": "Please review.",
            },
            notifier=Mock(),
        )

        updated = update_application(application.id, {"status": "accepted"})

        assert updated.status == "accepted"
        assert db.session.get(Application, application.id).status == "accepted"


def test_delete_opportunity_cascades_applications(app):
    with app.app_context():
        opportunity = create_opportunity(
            {
                "title": "Delete Me",
                "company": "Archive Corp",
                "location": "Remote",
                "description": "Temporary role.",
            },
            notifier=Mock(),
        )
        application = submit_application(
            opportunity.id,
            {
                "applicant_name": "Delete Candidate",
                "email": "delete@example.com",
                "resume_text": "Temporary application.",
                "cover_letter": "Temporary application.",
            },
            notifier=Mock(),
        )
        application_id = application.id

        delete_opportunity(opportunity.id)

        assert db.session.get(Opportunity, opportunity.id) is None
        assert db.session.get(Application, application_id) is None
