from flask import Blueprint, flash, redirect, render_template, request, url_for

from .services import (
    ValidationError,
    create_opportunity,
    delete_opportunity,
    get_opportunity_or_404,
    list_open_opportunities,
    submit_application,
)


web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def home():
    return render_template("index.html", opportunities=list_open_opportunities())


@web_bp.route("/opportunities/new", methods=["GET", "POST"])
def create_opportunity_view():
    if request.method == "POST":
        try:
            opportunity = create_opportunity(request.form)
        except ValidationError as exc:
            flash(str(exc), "error")
            return render_template("opportunity_form.html"), 400

        flash("Opportunity posted successfully.", "success")
        return redirect(url_for("web.opportunity_detail", opportunity_id=opportunity.id))

    return render_template("opportunity_form.html")


@web_bp.route("/opportunities/<int:opportunity_id>")
def opportunity_detail(opportunity_id: int):
    opportunity = get_opportunity_or_404(opportunity_id)
    return render_template("opportunity_detail.html", opportunity=opportunity)


@web_bp.route("/opportunities/<int:opportunity_id>/apply", methods=["POST"])
def apply_to_opportunity(opportunity_id: int):
    try:
        submit_application(opportunity_id, request.form)
    except ValidationError as exc:
        flash(str(exc), "error")
        return redirect(url_for("web.opportunity_detail", opportunity_id=opportunity_id))

    flash("Application submitted successfully.", "success")
    return redirect(url_for("web.opportunity_detail", opportunity_id=opportunity_id))


@web_bp.route("/opportunities/<int:opportunity_id>/delete", methods=["POST"])
def delete_opportunity_view(opportunity_id: int):
    delete_opportunity(opportunity_id)
    flash("Opportunity deleted successfully.", "success")
    return redirect(url_for("web.home"))
