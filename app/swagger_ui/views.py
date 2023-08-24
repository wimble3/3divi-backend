from app.swagger_ui.helpers import create_spec

from flask import Blueprint, jsonify

from flask_swagger_ui import get_swaggerui_blueprint


bp = Blueprint("swagger", __name__, url_prefix="/api")

# swagger urls
SWAGGER_URL = "/api/docs/"
API_URL = "/api/swagger/"

# registration swagger urls
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "App"}
)


@bp.route("/swagger/")
def create_swagger_spec():
    """
    Creates swagger doc and convert it to JSON.

    Returns:
        None:
    """
    spec = create_spec()
    return jsonify(spec.to_dict())
