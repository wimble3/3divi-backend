from app import app

from flask import Blueprint

from settings import DEBUG, HOST, PORT

bp = Blueprint("server", __name__)


@bp.cli.command("run", help="run server")
def run():
    app.run(host=HOST, port=PORT, debug=DEBUG)
