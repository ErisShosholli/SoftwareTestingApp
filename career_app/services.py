from __future__ import annotations

import re
from typing import Any

from flask import abort
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import Application, Opportunity, User


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
OPPORTUNITY_STATUSES = {"open", "closed"}
EMPLOYMENT_TYPES = {
    "Full-time",
    "Part-time",
    "Contract",
    "Internship",
    "Temporary",
}
APPLICATION_STATUSES = {"submitted", "reviewing", "accepted", "rejected"}
USER_ROLES = {"candidate", "recruiter"}


class ValidationError(ValueError):
    pass


class ConflictError(ValueError):
    pass


def validate_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError("A JSON object is required.")
    return payload


def validate_required_fields(payload: dict[str, Any], fields: list[str]) -> None:
    missing = [field for field in fields if not str(payload.get(field, "")).strip()]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")


def validate_email(email: str) -> str:
    normalized = email.strip().lower()
    if not EMAIL_PATTERN.match(normalized):
        raise ValidationError("A valid email address is required.")
    return normalized


def validate_choice(value: str, allowed: set[str], field_name: str) -> str:
    normalized = value.strip()
    if normalized not in allowed:
        options = ", ".join(sorted(allowed))
        raise ValidationError(f"{field_name} must be one of: {options}.")
    return normalized


def send_notification(subject: str, recipient: str) -> str:
    return f"Notification queued for {recipient}: {subject}"


def serialize_user(user: User, include_token: bool = False) -> dict[str, Any]:
    result = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at.isoformat(),
    }
    if include_token:
        result["token"] = user.api_token
    return result


def serialize_opportunity(opportunity: Opportunity) -> dict[str, Any]:
    return {
        "id": opportunity.id,
        "title": opportunity.title,
        "company": opportunity.company,
        "location": opportunity.location,
        "description": opportunity.description,
        "status": opportunity.status,
        "employment_type": opportunity.employment_type,
        "application_count": len(opportunity.applications),
        "created_at": opportunity.created_at.isoformat(),
    }


def serialize_application(application: Application) -> dict[str, Any]:
    return {
        "id": application.id,
        "applicant_name": application.applicant_name,
        "email": application.email,
        "resume_text": application.resume_text,
        "cover_letter": application.cover_letter,
        "status": application.status,
        "opportunity_id": application.opportunity_id,
        "created_at": application.created_at.isoformat(),
    }


def register_user(payload: dict[str, Any]) -> User:
    payload = validate_payload(payload)
    validate_required_fields(payload, ["name", "email", "password", "role"])

    password = str(payload["password"])
    if len(password) < 8:
        raise ValidationError("Password must contain at least 8 characters.")

    user = User(
        name=str(payload["name"]).strip(),
        email=validate_email(str(payload["email"])),
        role=validate_choice(str(payload["role"]).lower(), USER_ROLES, "role"),
        api_token="pending",
    )
    user.set_password(password)
    user.rotate_token()
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ConflictError("A user with this email already exists.") from exc
    return user


def authenticate_user(payload: dict[str, Any]) -> User:
    payload = validate_payload(payload)
    validate_required_fields(payload, ["email", "password"])
    email = validate_email(str(payload["email"]))
    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(str(payload["password"])):
        raise ValidationError("Invalid email or password.")
    user.rotate_token()
    db.session.commit()
    return user


def update_user(user: User, payload: dict[str, Any]) -> User:
    payload = validate_payload(payload)
    if "name" in payload:
        name = str(payload["name"]).strip()
        if not name:
            raise ValidationError("name cannot be empty.")
        user.name = name
    if "password" in payload:
        password = str(payload["password"])
        if len(password) < 8:
            raise ValidationError("Password must contain at least 8 characters.")
        user.set_password(password)
    if not {"name", "password"} & payload.keys():
        raise ValidationError("Provide name or password to update.")
    db.session.commit()
    return user


def delete_user(user: User) -> None:
    db.session.delete(user)
    db.session.commit()


def create_opportunity(
    payload: dict[str, Any],
    notifier=send_notification,
) -> Opportunity:
    payload = validate_payload(payload)
    validate_required_fields(payload, ["title", "company", "location", "description"])

    status = validate_choice(
        str(payload.get("status", "open")).lower(),
        OPPORTUNITY_STATUSES,
        "status",
    )
    employment_type = validate_choice(
        str(payload.get("employment_type", "Full-time")),
        EMPLOYMENT_TYPES,
        "employment_type",
    )
    opportunity = Opportunity(
        title=str(payload["title"]).strip(),
        company=str(payload["company"]).strip(),
        location=str(payload["location"]).strip(),
        description=str(payload["description"]).strip(),
        status=status,
        employment_type=employment_type,
    )
    db.session.add(opportunity)
    db.session.commit()
    notifier("New opportunity created", opportunity.company)
    return opportunity


def list_open_opportunities() -> list[Opportunity]:
    return (
        Opportunity.query.filter_by(status="open")
        .order_by(Opportunity.created_at.desc())
        .all()
    )


def get_opportunity_or_404(opportunity_id: int) -> Opportunity:
    opportunity = db.session.get(Opportunity, opportunity_id)
    if not opportunity:
        abort(404, description="Opportunity not found.")
    return opportunity


def update_opportunity(
    opportunity_id: int,
    payload: dict[str, Any],
) -> Opportunity:
    payload = validate_payload(payload)
    opportunity = get_opportunity_or_404(opportunity_id)
    editable = {
        "title",
        "company",
        "location",
        "description",
        "status",
        "employment_type",
    }
    supplied = editable & payload.keys()
    if not supplied:
        raise ValidationError("No editable opportunity fields were provided.")

    for field in {"title", "company", "location", "description"} & supplied:
        value = str(payload[field]).strip()
        if not value:
            raise ValidationError(f"{field} cannot be empty.")
        setattr(opportunity, field, value)
    if "status" in supplied:
        opportunity.status = validate_choice(
            str(payload["status"]).lower(),
            OPPORTUNITY_STATUSES,
            "status",
        )
    if "employment_type" in supplied:
        opportunity.employment_type = validate_choice(
            str(payload["employment_type"]),
            EMPLOYMENT_TYPES,
            "employment_type",
        )
    db.session.commit()
    return opportunity


def delete_opportunity(opportunity_id: int) -> None:
    opportunity = get_opportunity_or_404(opportunity_id)
    db.session.delete(opportunity)
    db.session.commit()


def submit_application(
    opportunity_id: int,
    payload: dict[str, Any],
    notifier=send_notification,
) -> Application:
    payload = validate_payload(payload)
    validate_required_fields(
        payload,
        ["applicant_name", "email", "resume_text", "cover_letter"],
    )
    opportunity = get_opportunity_or_404(opportunity_id)
    if opportunity.status != "open":
        raise ValidationError("Applications are closed for this opportunity.")

    email = validate_email(str(payload["email"]))
    existing = Application.query.filter_by(
        opportunity_id=opportunity_id,
        email=email,
    ).first()
    if existing:
        raise ConflictError("This email has already applied for this opportunity.")

    application = Application(
        applicant_name=str(payload["applicant_name"]).strip(),
        email=email,
        resume_text=str(payload["resume_text"]).strip(),
        cover_letter=str(payload["cover_letter"]).strip(),
        status="submitted",
        opportunity=opportunity,
    )
    db.session.add(application)
    db.session.commit()
    notifier("New application submitted", application.email)
    return application


def get_application_or_404(application_id: int) -> Application:
    application = db.session.get(Application, application_id)
    if not application:
        abort(404, description="Application not found.")
    return application


def update_application(
    application_id: int,
    payload: dict[str, Any],
) -> Application:
    payload = validate_payload(payload)
    application = get_application_or_404(application_id)
    editable = {
        "applicant_name",
        "email",
        "resume_text",
        "cover_letter",
        "status",
    }
    supplied = editable & payload.keys()
    if not supplied:
        raise ValidationError("No editable application fields were provided.")

    for field in {"applicant_name", "resume_text", "cover_letter"} & supplied:
        value = str(payload[field]).strip()
        if not value:
            raise ValidationError(f"{field} cannot be empty.")
        setattr(application, field, value)
    if "email" in supplied:
        application.email = validate_email(str(payload["email"]))
    if "status" in supplied:
        application.status = validate_choice(
            str(payload["status"]).lower(),
            APPLICATION_STATUSES,
            "status",
        )
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ConflictError(
            "This email has already applied for this opportunity."
        ) from exc
    return application


def delete_application(application_id: int) -> None:
    application = get_application_or_404(application_id)
    db.session.delete(application)
    db.session.commit()
