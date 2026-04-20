from unittest.mock import Mock, patch

import pytest

from career_app.extensions import db
from career_app.models import Opportunity
from career_app.services import ValidationError, create_opportunity, delete_opportunity, submit_application


def test_create_opportunity_persists_record_and_notifies(app):
    notifier = Mock()

    with app.app_context():
        opportunity = create_opportunity(
            {
                "title": "QA Engineer",
                "company": "Dracula Labs",
                "location": "Remote",
                "description": "Own testing strategy.",
            },
            notifier=notifier,
        )

        saved = Opportunity.query.get(opportunity.id)
        assert saved is not None
        assert saved.company == "Dracula Labs"
        notifier.assert_called_once_with("New opportunity created", "Dracula Labs")


def test_create_opportunity_rejects_missing_fields(app):
    with app.app_context():
        with pytest.raises(ValidationError):
            create_opportunity({"title": "", "company": "Acme"}, notifier=Mock())


def test_submit_application_uses_default_notification_patch(app):
    with app.app_context():
        opportunity = Opportunity(
            title="Backend Developer",
            company="Acme",
            location="Prishtina",
            description="Build APIs.",
        )
        db.session.add(opportunity)
        db.session.commit()

        with patch("career_app.services.send_notification") as mocked_notification:
            application = submit_application(
                opportunity.id,
                {
                    "applicant_name": "Lina Test",
                    "email": "lina@example.com",
                    "resume_text": "3 years in Python.",
                    "cover_letter": "I enjoy reliable systems.",
                },
                notifier=mocked_notification,
            )

            assert application.id is not None
            mocked_notification.assert_called_once_with(
                "New application submitted",
                "lina@example.com",
            )


def test_submit_application_rejects_closed_opportunity(app):
    with app.app_context():
        opportunity = Opportunity(
            title="SDET",
            company="North Wind",
            location="Remote",
            description="Test pipelines.",
            status="closed",
        )
        db.session.add(opportunity)
        db.session.commit()

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


def test_delete_opportunity_removes_record(app):
    with app.app_context():
        opportunity = Opportunity(
            title="Delete Me",
            company="Archive Corp",
            location="Remote",
            description="Temporary role.",
        )
        db.session.add(opportunity)
        db.session.commit()

        delete_opportunity(opportunity.id)

        assert Opportunity.query.get(opportunity.id) is None
