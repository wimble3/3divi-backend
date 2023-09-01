from aiohttp import web

from flask import Flask
from flask_alembic import Alembic

from flask_cors import CORS

from flask_marshmallow import Marshmallow

from flask_sqlalchemy import SQLAlchemy

from app.api.helpers.services import RedisService
from settings import ACCESS_CONTROL_ALLOW_CREDENTIALS


# App
app = Flask(__name__)
app.config.from_object("settings")
aioapp = web.Application()

# Database
db = SQLAlchemy(app)

# Alembic
alembic = Alembic()
alembic.init_app(app)

# Marshmallow
ma = Marshmallow(app)

# Adding CORS for api resource. All origins
CORS(app, resources={r"/api/*": {"origins": "*"}},
     supports_credentials=ACCESS_CONTROL_ALLOW_CREDENTIALS)

# Redis service
redis_service = RedisService()

# Events
from app.api.events import *  # noqa: E402, I100, E501, I202, F401

# Routing
from app.api.videos.views import bp as bp__videos  # noqa: E402, I100, E501, I202
app.register_blueprint(bp__videos)


# Adding swagger
from app.swagger_ui.views import (bp as swagger, swagger_ui_blueprint as swagger_ui)  # noqa: E402, I100, E501, I202

app.register_blueprint(swagger)
app.register_blueprint(swagger_ui)
