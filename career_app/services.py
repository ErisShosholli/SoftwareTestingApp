from __future__ import annotations

from typing import Any

from flask import abort

from .extensions import db
from .models import Application, Opportunity


class ValidationError(ValueError):
    pass


def validate_required_fields(payload: dict[str, Any], fields: list[str]) -> None:
    missing = [field for field in fields if not str(payload.get(field, "")).strip()]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")


def send_notification(subject: str, recipient: str) -> str:
    return f"Notification queued for {recipient}: {subject}"


def serialize_opportunity(opportunity: Opportunity) -> dict[str, Any]:
    return {
        "id": opportunity.id,
        "title": opportunity.title,
        "company": opportunity.company,
        "location": opportunity.location,
        "description": opportunity.description,
        "status": opportunity.status,
        "application_count": len(opportunity.applications),
    }


def serialize_application(application: Application) -> dict[str, Any]:
    return {
        "id": application.id,
        "applicant_name": application.applicant_name,
        "email": application.email,
        "resume_text": application.resume_text,
        "cover_letter": application.cover_letter,
        "opportunity_id": application.opportunity_id,
    }


def create_opportunity(payload: dict[str, Any], notifier=send_notification) -> Opportunity:
    validate_required_fields(payload, ["title", "company", "location", "description"])

    opportunity = Opportunity(
        title=payload["title"].strip(),
        company=payload["company"].strip(),
        location=payload["location"].strip(),
        description=payload["description"].strip(),
        status=payload.get("status", "open").strip() or "open",
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
    opportunity = Opportunity.query.get(opportunity_id)
    if not opportunity:
        abort(404, description="Opportunity not found.")
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
    validate_required_fields(
        payload,
        ["applicant_name", "email", "resume_text", "cover_letter"],
    )
    opportunity = get_opportunity_or_404(opportunity_id)
    if opportunity.status != "open":
        raise ValidationError("Applications are closed for this opportunity.")

    application = Application(
        applicant_name=payload["applicant_name"].strip(),
        email=payload["email"].strip(),
        resume_text=payload["resume_text"].strip(),
        cover_letter=payload["cover_letter"].strip(),
        opportunity=opportunity,
    )
    db.session.add(application)
    db.session.commit()
    notifier("New application submitted", application.email)
    return application
