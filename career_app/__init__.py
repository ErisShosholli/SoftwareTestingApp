import os

from flask import Flask
from sqlalchemy import inspect, text

from .api import api_bp
from .extensions import db
from .routes import web_bp


def ensure_legacy_schema():
    inspector = inspect(db.engine)
    tables = set(inspector.get_table_names())

    if "opportunities" in tables:
        columns = {column["name"] for column in inspector.get_columns("opportunities")}
        if "employment_type" not in columns:
            db.session.execute(
                text(
                    "ALTER TABLE opportunities ADD COLUMN employment_type "
                    "VARCHAR(40) NOT NULL DEFAULT 'Full-time'"
                )
            )

    if "applications" in tables:
        columns = {column["name"] for column in inspector.get_columns("applications")}
        if "status" not in columns:
            db.session.execute(
                text(
                    "ALTER TABLE applications ADD COLUMN status "
                    "VARCHAR(20) NOT NULL DEFAULT 'submitted'"
                )
            )
    db.session.commit()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL",
            "sqlite:///career_app.db",
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        TESTING=False,
    )

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        from . import models  # noqa: F401

        db.create_all()
        ensure_legacy_schema()

    return app
