import os

from flask import Flask

from config import Config
from db import init_db
from routes.ui_removals import ui_removals_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_db(app)  # stores the VectorAI base URL; collection created lazily on first request

    app.register_blueprint(ui_removals_bp, url_prefix="/api")

    @app.errorhandler(404)
    def not_found(e):
        return {"data": None, "error": "Resource not found"}, 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return {"data": None, "error": "Method not allowed"}, 405

    @app.errorhandler(Exception)
    def unhandled(e):
        app.logger.exception("Unhandled exception")
        return {"data": None, "error": "Internal server error"}, 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
