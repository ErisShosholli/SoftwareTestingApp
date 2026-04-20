# Software Testing Project Report

## 1. Overview

This project implements **CareerFlow**, a Python web application for managing career opportunities and job applications. The application was developed with testability as a core design goal. Business rules are placed in a service layer, persistence is handled through SQLAlchemy models, and both HTML and REST API interfaces are exposed for end users and external clients.

## 2. Objectives Achieved

- Developed a web application for posting and applying to career opportunities
- Implemented a REST API for key operations
- Designed and executed unit, integration, system, and API tests
- Used mocks and patches to isolate side effects during testing
- Produced documentation describing the testing strategy and outcomes

## 3. Technology Choices

### Application Stack

- **Flask**: lightweight and appropriate for a small, testable course project
- **Flask-SQLAlchemy**: simplifies persistence and supports isolated in-memory testing
- **SQLite**: fast setup for local development and test environments

### Testing Stack

- **pytest**: concise syntax, fixtures, and strong plugin ecosystem
- **pytest-cov**: coverage reporting for measuring test reach
- **unittest.mock**: built-in mocking and patching support for isolating dependencies

These tools were selected because they reduce boilerplate, speed up feedback, and are widely used in Python testing practice.

## 4. Application Design

The application contains two main domain entities:

- **Opportunity**: stores job title, company, location, description, status, and related applications
- **Application**: stores applicant details and links each application to an opportunity

The architecture is intentionally split into layers:

- **Routes**: handle HTTP requests and HTML rendering
- **API Blueprint**: returns JSON responses for REST consumers
- **Services**: contains validation, creation logic, submission rules, and serialization
- **Models**: define persistence structure

This separation improves maintainability and makes unit testing more effective.

## 5. Test Plan

### Scope

The test plan covers:

- Unit testing of service and validation functions
- Integration testing of route/database interaction
- System testing of the complete user workflow
- REST API testing for endpoint correctness and error handling

### Strategy by Test Type

#### Unit Tests

Goal:
Verify individual units of logic in isolation.

Covered areas:

- Required field validation
- Opportunity creation behavior
- Application submission rules
- Closed opportunity rejection
- Notification side effect isolation using mocks

#### Integration Tests

Goal:
Ensure multiple components work correctly together.

Covered areas:

- Posting an opportunity through the web route and confirming database persistence
- Submitting an application through the web route and confirming relational data storage
- Returning validation feedback from form submissions

#### System Tests

Goal:
Validate the full application behavior from the user perspective.

Covered scenario:

1. Recruiter creates a new opportunity
2. Candidate views the homepage
3. Candidate opens the detail page workflow
4. Candidate submits an application successfully

#### REST API Tests

Goal:
Confirm API reliability, data accuracy, and proper error handling.

Covered endpoints:

- `GET /api/opportunities`
- `POST /api/opportunities`
- `GET /api/opportunities/<id>`
- `POST /api/opportunities/<id>/apply`

Test assertions include:

- Correct HTTP status codes
- Proper JSON response structure
- Application creation behavior
- Validation error messages for malformed requests

## 6. Mocks and Patches

Mocks and patches were used to avoid coupling tests to external side effects.

Examples:

- A mock notifier verifies that opportunity creation triggers a notification call
- A patch on `send_notification` demonstrates isolation of the default notification dependency

This makes tests faster, more focused, and more reliable.

## 7. Challenges and Solutions

### Challenge 1: Keeping the application testable

If business logic is written directly inside routes, unit testing becomes difficult.

Solution:
Validation and persistence rules were extracted into `services.py`, making them easy to test independently from the web framework.

### Challenge 2: Testing realistic workflows without browser automation

Full browser tools would add unnecessary complexity for this assignment.

Solution:
System-style tests were implemented with Flask's test client to simulate complete user journeys while keeping setup lightweight.

### Challenge 3: Verifying side effects without creating real integrations

Direct email or notification systems were unnecessary for the assignment.

Solution:
Mocks and patches were applied to verify behavior without requiring external services.

## 8. Test Outcomes

The test suite demonstrates that:

- Core business rules behave as expected
- Web routes integrate correctly with the database
- End-to-end workflows succeed for the primary use case
- API endpoints return correct responses and handle invalid data safely

Because the application uses an in-memory SQLite database during tests, each test runs in a clean isolated environment, improving repeatability.

## 9. UI Design

The user interface uses a **Dracula theme** with:

- dark layered backgrounds
- magenta, purple, and cyan highlights
- responsive card-based layout
- visually distinct forms and success/error feedback

The design goal was to keep the interface clean, modern, and readable while matching the assignment request.

## 10. Conclusion

This project satisfies the assignment requirements by delivering:

- a functional Python career opportunity management web application
- a REST API for essential operations
- a complete multi-layered test suite
- mock and patch usage
- documentation of methods, tools, challenges, and outcomes

The resulting project demonstrates both software development and testing practice in a structured, maintainable way.
