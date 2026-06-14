from datetime import UTC, datetime
from secrets import token_urlsafe

from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def utc_now():
    return datetime.now(UTC)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="candidate")
    api_token = db.Column(db.String(255), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def rotate_token(self):
        self.api_token = token_urlsafe(32)
        return self.api_token


class Opportunity(db.Model):
    __tablename__ = "opportunities"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="open")
    employment_type = db.Column(
        db.String(40),
        nullable=False,
        default="Full-time",
        server_default="Full-time",
    )
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    applications = db.relationship(
        "Application",
        back_populates="opportunity",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Application(db.Model):
    __tablename__ = "applications"
    __table_args__ = (
        db.UniqueConstraint(
            "email",
            "opportunity_id",
            name="uq_application_email_opportunity",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    applicant_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    resume_text = db.Column(db.Text, nullable=False)
    cover_letter = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.String(20),
        nullable=False,
        default="submitted",
        server_default="submitted",
    )
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    opportunity_id = db.Column(
        db.Integer,
        db.ForeignKey("opportunities.id"),
        nullable=False,
    )

    opportunity = db.relationship("Opportunity", back_populates="applications")
