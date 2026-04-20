import pytest

from career_app.services import ValidationError, validate_required_fields


def test_validate_required_fields_accepts_complete_payload():
    validate_required_fields({"title": "QA", "company": "Acme"}, ["title", "company"])


def test_validate_required_fields_reports_missing_items():
    with pytest.raises(ValidationError) as exc:
        validate_required_fields({"title": "QA", "company": "  "}, ["title", "company", "location"])

    assert "company, location" in str(exc.value)
