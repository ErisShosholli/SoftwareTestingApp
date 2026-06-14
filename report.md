# CareerFlow Assignment 2 Report

## Overview

CareerFlow extends the Assignment 1 career opportunity application with a
larger REST API, authentication, model changes, database compatibility, and
multi-level automated testing. The application uses Flask, SQLAlchemy,
Flask-RESTful, SQLite, pytest, Postman, and Newman.

## API and Model Extensions

The original `Opportunity` and `Application` models remain the central domain
entities. The following changes were implemented:

- `User` stores name, normalized email, hashed password, role, API token, and
  creation time.
- `Opportunity.employment_type` is the required modified-model field.
- `Application.status` supports `submitted`, `reviewing`, `accepted`, and
  `rejected` workflow states.
- The existing one-to-many relationship between opportunities and
  applications uses cascade deletion.
- Duplicate applications from the same email to the same opportunity are
  rejected.

The Flask-RESTful API provides registration/login, current-user CRUD,
opportunity CRUD, application CRUD, per-opportunity application listing, and a
health endpoint.

## Authentication

Passwords are stored with Werkzeug password hashing. Registration and login
return a random API token. Protected calls require:

```text
Authorization: Bearer <token>
```

All opportunity and application `POST` operations after account creation, and
all resource `PUT` and `DELETE` methods, require authentication. Invalid or
missing tokens return HTTP `401`.

## Database

SQLite is used for development and in-memory SQLite is used during pytest
runs. `db.create_all()` executes during application creation, before the first
request is served.

For compatibility with the Assignment 1 database, startup schema inspection
adds `Opportunity.employment_type` and `Application.status` when those columns
are absent. New installations receive the complete schema immediately.

## Testing Strategy

### Unit Tests

Unit tests cover:

- required-field, email, JSON, and choice validation
- password hashing and token rotation
- the new `employment_type` model field
- opportunity/application relationships
- service persistence and notification mocks
- closed opportunities and duplicate applications
- opportunity and application status updates
- cascade deletion

### Integration and API Tests

Integration tests verify web routes, SQLAlchemy persistence, model
relationships, and the new UI/model field. API tests verify:

- registration, login, duplicate users, and invalid credentials
- authenticated user read/update/delete
- authentication enforcement on protected methods
- complete opportunity CRUD
- complete application CRUD
- validation, conflicts, status codes, and JSON response content

### System Tests

The pytest system journey registers recruiter and candidate users, creates a
contract opportunity, submits an application, accepts it, and confirms the
opportunity application count. A separate browser-style Flask client journey
tests the HTML posting and application flow.

The Postman collection executes the complete external workflow in order. It
contains collection-wide response-time and JSON checks plus endpoint-specific
status and data assertions.

## Verified Results

- pytest: 39 tests passed
- Python coverage: 94%
- Newman/Postman: 22 requests passed
- Postman assertions: 91 passed, 0 failed
- Average local API response time during the recorded Newman run: 85 ms

Evidence is stored in `screenshots/` and `tests/system/`.

## Conclusion

The project now satisfies the Assignment 2 requirements for Flask-RESTful
resources, SQLite/SQLAlchemy persistence, protected mutations, a modified
existing model, CRUD workflows, Postman system testing, and organized unit,
integration, API, and system test suites.
