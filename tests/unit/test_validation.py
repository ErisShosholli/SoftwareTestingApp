import pytest

from career_app.services import (
    ValidationError,
    validate_choice,
    validate_email,
    validate_payload,
    validate_required_fields,
)


def test_validate_required_fields_accepts_complete_payload():
    validate_required_fields(
        {"title": "QA", "company": "Acme"},
        ["title", "company"],
    )


def test_validate_required_fields_reports_all_missing_items():
    with pytest.raises(ValidationError) as exc:
        validate_required_fields(
            {"title": "QA", "company": "  "},
            ["title", "company", "location"],
        )

    assert "company, location" in str(exc.value)


def test_validate_email_normalizes_valid_address():
    assert validate_email("  Person@Example.COM ") == "person@example.com"


def test_validate_email_rejects_invalid_address():
    with pytest.raises(ValidationError, match="valid email"):
        validate_email("not-an-email")


def test_validate_choice_reports_allowed_values():
    with pytest.raises(ValidationError, match="Full-time"):
        validate_choice("Freelance", {"Full-time", "Contract"}, "employment_type")


def test_validate_payload_rejects_non_object_json():
    with pytest.raises(ValidationError, match="JSON object"):
        validate_payload(["not", "an", "object"])
