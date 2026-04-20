# CareerFlow Testing Project

CareerFlow is a Flask-based career opportunity management web application created for a software testing course assignment. It allows recruiters to post opportunities, candidates to apply through the web interface, and external clients to manage data through a REST API.

## Features

- Dracula-themed responsive UI for posting and viewing opportunities
- Delete job support in both the web UI and REST API
- HTML workflow for job creation and candidate applications
- REST API for listing, creating, and applying to opportunities
- Service layer that keeps business logic isolated and easy to test
- Unit, integration, system, and API tests implemented with `pytest`
- Mocking and patching examples for notification behavior

## Project Structure

```text
career_app/
  __init__.py
  api.py
  extensions.py
  models.py
  routes.py
  services.py
  static/style.css
  templates/
tests/
  api/
  integration/
  system/
  unit/
run.py
report.md
requirements.txt
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

The application starts at `http://127.0.0.1:5000/`.

## Running Tests

```bash
pytest --maxfail=1 --disable-warnings --cov=career_app --cov-report=term-missing
```

## REST API Endpoints

- `GET /api/opportunities`
- `POST /api/opportunities`
- `GET /api/opportunities/<id>`
- `DELETE /api/opportunities/<id>`
- `POST /api/opportunities/<id>/apply`

## Testing Highlights

- Unit tests validate service functions and field validation.
- Integration tests verify route-to-database workflows.
- System tests simulate a complete recruiter and candidate journey.
- API tests confirm status codes, JSON payloads, and error handling.
- Mocks and patches isolate notification behavior from the persistence flow.
