from flask import Flask

from .api import api_bp
from .extensions import db
from .routes import web_bp


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_mapping(
        SECRET_KEY="dev-secret-key",
        SQLALCHEMY_DATABASE_URI="sqlite:///career_app.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        TESTING=False,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        from . import models  # noqa: F401

        db.create_all()

    return app
