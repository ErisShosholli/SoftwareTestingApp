# CareerFlow Career Opportunity API

CareerFlow is a Flask career opportunity management application with a web UI,
SQLite persistence, a Flask-RESTful API, bearer-token authentication, and
unit, integration, API, system, and Postman tests.

## Assignment Changes

- Added a `User` model with hashed passwords, roles, and API tokens.
- Modified `Opportunity` with the new `employment_type` field.
- Added `status` to `Application` for review workflows.
- Added authenticated CRUD resources for users, opportunities, and applications.
- Added duplicate-application, email, status, and employment-type validation.
- Added automatic SQLite table creation and legacy-column upgrades at startup.
- Added comprehensive pytest and Postman/Newman test suites.

## Project Structure

```text
career_app/
  __init__.py
  api.py
  auth.py
  extensions.py
  models.py
  routes.py
  services.py
  static/
  templates/
postman/
  CareerFlow.postman_collection.json
  CareerFlow.postman_environment.json
screenshots/
tests/
  api/
  integration/
  system/
  unit/
run.py
requirements.txt
```

## Setup

Python 3.11 or newer is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```

Open the web application at `http://127.0.0.1:5000/` and the API health
endpoint at `http://127.0.0.1:5000/api/health`.

The development database is created automatically at
`instance/career_app.db`. Existing Assignment 1 databases are upgraded with
the `employment_type` and application `status` columns when the app starts.

Optional configuration:

```powershell
$env:SECRET_KEY = "replace-for-production"
$env:DATABASE_URL = "sqlite:///career_app.db"
```

## Authentication

Register or log in to receive a token, then send it on protected requests:

```text
Authorization: Bearer <token>
```

Registration and login are public. Opportunity/application creation, all
`PUT` and `DELETE` operations, and application/user reads are protected.

## API Endpoints

| Method | Endpoint | Authentication |
|---|---|---|
| `GET` | `/api/health` | Public |
| `POST` | `/api/auth/register` | Public |
| `POST` | `/api/auth/login` | Public |
| `GET`, `PUT`, `DELETE` | `/api/users/me` | Required |
| `GET` | `/api/opportunities` | Public |
| `POST` | `/api/opportunities` | Required |
| `GET` | `/api/opportunities/<id>` | Public |
| `PUT`, `DELETE` | `/api/opportunities/<id>` | Required |
| `GET`, `POST` | `/api/opportunities/<id>/applications` | Required |
| `POST` | `/api/opportunities/<id>/apply` | Required |
| `GET` | `/api/applications` | Required |
| `GET`, `PUT`, `DELETE` | `/api/applications/<id>` | Required |

Allowed employment types are `Full-time`, `Part-time`, `Contract`,
`Internship`, and `Temporary`.

## Pytest Suite

```powershell
python -m pytest --disable-warnings --cov=career_app --cov-report=term-missing
```

The suite is organized by level:

- `tests/unit`: models, validation, and service functions
- `tests/integration`: web routes and database relationships
- `tests/api`: authentication and REST resource behavior
- `tests/system`: complete recruiter/candidate workflows

Current verified result: **39 passed, 94% coverage**.

## Postman System Tests

1. Start the application with `python run.py`.
2. Import both JSON files from `postman/` into Postman.
3. Select the **CareerFlow Local** environment.
4. Run **CareerFlow API System Tests** with the Collection Runner.

The collection creates unique users for each run and tests all API resources,
status codes, response data, authentication failures, the modified
`employment_type` field, duplicate applications, and response times.

Newman command-line execution:

```powershell
npx newman run postman\CareerFlow.postman_collection.json `
  --environment postman\CareerFlow.postman_environment.json
```

Current verified result: **22 requests, 91 assertions, 0 failures**.

## Test Evidence

- `screenshots/pytest-results.png`
- `screenshots/postman-results.png`
- `tests/system/postman-results.xml`
- `tests/system/pytest-output.txt`
- `tests/system/newman-output.txt`
