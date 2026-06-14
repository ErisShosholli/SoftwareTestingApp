import sqlite3

from sqlalchemy import inspect

from career_app import create_app
from career_app.extensions import db


def test_legacy_sqlite_schema_receives_new_columns(tmp_path):
    database_path = tmp_path / "legacy.db"
    connection = sqlite3.connect(database_path)
    connection.executescript(
        """
        CREATE TABLE opportunities (
            id INTEGER PRIMARY KEY,
            title VARCHAR(120) NOT NULL,
            company VARCHAR(120) NOT NULL,
            location VARCHAR(120) NOT NULL,
            description TEXT NOT NULL,
            status VARCHAR(20) NOT NULL,
            created_at DATETIME NOT NULL
        );
        CREATE TABLE applications (
            id INTEGER PRIMARY KEY,
            applicant_name VARCHAR(120) NOT NULL,
            email VARCHAR(120) NOT NULL,
            resume_text TEXT NOT NULL,
            cover_letter TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            opportunity_id INTEGER NOT NULL
        );
        """
    )
    connection.close()

    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path.as_posix()}",
        }
    )

    with app.app_context():
        inspector = inspect(db.engine)
        opportunity_columns = {
            column["name"] for column in inspector.get_columns("opportunities")
        }
        application_columns = {
            column["name"] for column in inspector.get_columns("applications")
        }

    assert "employment_type" in opportunity_columns
    assert "status" in application_columns
