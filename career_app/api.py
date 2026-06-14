from functools import wraps

from flask import Blueprint, g, request
from flask_restful import Api, Resource

from .auth import token_required
from .extensions import db
from .models import Application, Opportunity
from .services import (
    ConflictError,
    ValidationError,
    authenticate_user,
    create_opportunity,
    delete_application,
    delete_opportunity,
    delete_user,
    get_application_or_404,
    get_opportunity_or_404,
    register_user,
    serialize_application,
    serialize_opportunity,
    serialize_user,
    submit_application,
    update_application,
    update_opportunity,
    update_user,
)


api_bp = Blueprint("api", __name__)
rest_api = Api(api_bp)


def json_payload():
    return request.get_json(silent=True)


def service_errors(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        try:
            return view(*args, **kwargs)
        except ValidationError as exc:
            return {"error": str(exc)}, 400
        except ConflictError as exc:
            return {"error": str(exc)}, 409

    return wrapped


class HealthResource(Resource):
    def get(self):
        return {"status": "ok", "service": "CareerFlow API"}, 200


class RegisterResource(Resource):
    @service_errors
    def post(self):
        user = register_user(json_payload())
        return serialize_user(user, include_token=True), 201


class LoginResource(Resource):
    @service_errors
    def post(self):
        user = authenticate_user(json_payload())
        return serialize_user(user, include_token=True), 200


class CurrentUserResource(Resource):
    @token_required
    def get(self):
        return serialize_user(g.current_user), 200

    @token_required
    @service_errors
    def put(self):
        user = update_user(g.current_user, json_payload())
        return serialize_user(user), 200

    @token_required
    def delete(self):
        delete_user(g.current_user)
        return {"message": "User deleted successfully."}, 200


class OpportunityListResource(Resource):
    def get(self):
        opportunities = Opportunity.query.order_by(
            Opportunity.created_at.desc()
        ).all()
        return [serialize_opportunity(item) for item in opportunities], 200

    @token_required
    @service_errors
    def post(self):
        opportunity = create_opportunity(json_payload())
        return serialize_opportunity(opportunity), 201


class OpportunityResource(Resource):
    def get(self, opportunity_id):
        return serialize_opportunity(get_opportunity_or_404(opportunity_id)), 200

    @token_required
    @service_errors
    def put(self, opportunity_id):
        opportunity = update_opportunity(opportunity_id, json_payload())
        return serialize_opportunity(opportunity), 200

    @token_required
    def delete(self, opportunity_id):
        delete_opportunity(opportunity_id)
        return {"message": "Opportunity deleted successfully."}, 200


class OpportunityApplicationResource(Resource):
    @token_required
    def get(self, opportunity_id):
        get_opportunity_or_404(opportunity_id)
        applications = Application.query.filter_by(
            opportunity_id=opportunity_id
        ).order_by(Application.created_at.desc()).all()
        return [serialize_application(item) for item in applications], 200

    @token_required
    @service_errors
    def post(self, opportunity_id):
        application = submit_application(opportunity_id, json_payload())
        return serialize_application(application), 201


class ApplicationListResource(Resource):
    @token_required
    def get(self):
        applications = Application.query.order_by(
            Application.created_at.desc()
        ).all()
        return [serialize_application(item) for item in applications], 200


class ApplicationResource(Resource):
    @token_required
    def get(self, application_id):
        return serialize_application(get_application_or_404(application_id)), 200

    @token_required
    @service_errors
    def put(self, application_id):
        application = update_application(application_id, json_payload())
        return serialize_application(application), 200

    @token_required
    def delete(self, application_id):
        delete_application(application_id)
        return {"message": "Application deleted successfully."}, 200


rest_api.add_resource(HealthResource, "/health")
rest_api.add_resource(RegisterResource, "/auth/register")
rest_api.add_resource(LoginResource, "/auth/login")
rest_api.add_resource(CurrentUserResource, "/users/me")
rest_api.add_resource(OpportunityListResource, "/opportunities")
rest_api.add_resource(
    OpportunityResource,
    "/opportunities/<int:opportunity_id>",
)
rest_api.add_resource(
    OpportunityApplicationResource,
    "/opportunities/<int:opportunity_id>/applications",
    "/opportunities/<int:opportunity_id>/apply",
)
rest_api.add_resource(ApplicationListResource, "/applications")
rest_api.add_resource(
    ApplicationResource,
    "/applications/<int:application_id>",
)
