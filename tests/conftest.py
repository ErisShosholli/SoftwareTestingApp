import pytest

from career_app import create_app
from career_app.extensions import db


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
        }
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def register(client):
    counter = {"value": 0}

    def register_user(role="candidate", email=None):
        counter["value"] += 1
        user_email = email or f"{role}{counter['value']}@example.com"
        response = client.post(
            "/api/auth/register",
            json={
                "name": f"Test {role.title()}",
                "email": user_email,
                "password": "StrongPass123",
                "role": role,
            },
        )
        assert response.status_code == 201
        return response.get_json()

    return register_user


@pytest.fixture
def recruiter_headers(register):
    user = register(role="recruiter")
    return {"Authorization": f"Bearer {user['token']}"}


@pytest.fixture
def candidate_headers(register):
    user = register(role="candidate")
    return {"Authorization": f"Bearer {user['token']}"}


@pytest.fixture
def opportunity_payload():
    return {
        "title": "API Quality Engineer",
        "company": "Vector Labs",
        "location": "Remote",
        "description": "Build reliable API and integration test suites.",
        "employment_type": "Full-time",
    }


@pytest.fixture
def application_payload():
    return {
        "applicant_name": "Casey Candidate",
        "email": "casey@example.com",
        "resume_text": "Python, pytest, Postman, and SQL experience.",
        "cover_letter": "I enjoy making complex systems dependable.",
    }
