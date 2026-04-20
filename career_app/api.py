from flask import Blueprint, jsonify, request

from .services import (
    ValidationError,
    create_opportunity,
    delete_opportunity,
    get_opportunity_or_404,
    serialize_application,
    serialize_opportunity,
    submit_application,
)


api_bp = Blueprint("api", __name__)


@api_bp.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({"error": str(error)}), 400


@api_bp.route("/opportunities", methods=["GET"])
def list_opportunities_api():
    from .models import Opportunity

    opportunities = Opportunity.query.order_by(Opportunity.created_at.desc()).all()
    return jsonify([serialize_opportunity(opportunity) for opportunity in opportunities])


@api_bp.route("/opportunities", methods=["POST"])
def create_opportunity_api():
    opportunity = create_opportunity(request.get_json(force=True))
    return jsonify(serialize_opportunity(opportunity)), 201


@api_bp.route("/opportunities/<int:opportunity_id>", methods=["GET"])
def get_opportunity_api(opportunity_id: int):
    opportunity = get_opportunity_or_404(opportunity_id)
    return jsonify(serialize_opportunity(opportunity))


@api_bp.route("/opportunities/<int:opportunity_id>/apply", methods=["POST"])
def apply_to_opportunity_api(opportunity_id: int):
    application = submit_application(opportunity_id, request.get_json(force=True))
    return jsonify(serialize_application(application)), 201


@api_bp.route("/opportunities/<int:opportunity_id>", methods=["DELETE"])
def delete_opportunity_api(opportunity_id: int):
    delete_opportunity(opportunity_id)
    return jsonify({"message": "Opportunity deleted successfully."}), 200
