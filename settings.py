import configparser
import os
import sys

CONF_FILE = "local.conf"
# CONF_FILE = "dev.conf"

# Base settings
CURRENT_FILE_PATH = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(CURRENT_FILE_PATH)
APP_CONF = os.path.join(BASE_DIR, CONF_FILE)
LOGGING_CONF = BASE_DIR + "logging.yaml"

# Server config read
if os.path.isfile(APP_CONF) and os.access(APP_CONF, os.R_OK):
    _config = configparser.SafeConfigParser()
    _config.read(APP_CONF)
else:
    print(
        "ERROR: application config file '%s' not exists or not readable\n" %
        APP_CONF)
    sys.exit(1)

# Logger prefix
SLR_LOGGER_PREFIX = "app."

# Database
SQLALCHEMY_DATABASE_URI = _config.get("database", "uri")
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": _config.getint("database", "pool_size", fallback=50),
    "max_overflow": _config.getint("database", "max_overflow", fallback=150),
}
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False  # SQL debug
DATABASE_CONNECT_OPTIONS = {}
DB_TBL_PRFX = "app_"

# App
HOST = _config.get("app", "host", fallback="0.0.0.0")
PORT = _config.get("app", "port", fallback=5000)
SECRET_KEY = _config.get("app", "secret_key", fallback="No secret key")
DEBUG = _config.getboolean("app", "debug", fallback=False)
NUM_MAX_THREADS = _config.getint("app", "num_max_threads", fallback=8)
SWAGGER_FILENAME = "swagger-spec.yaml"
ACCESS_CONTROL_ALLOW_CREDENTIALS = True
ALLOWED_VIDEO_EXTENSIONS = ("mp4", "mov", "wmv", "avi", "flv", "mkv")

# Api spec
APISPEC_TITLE = _config.get(
    "apispec",
    "title",
    fallback="3divi_backend_video_processing"
)
APISPEC_VERSION = _config.get(
    "apispec",
    "apispec_version",
    fallback="v1"
)
APISPEC_OPENAPI_VER = _config.get(
    "apispec",
    "openapi_ver",
    fallback="3.0.3"
)
APISPEC_SERVER = _config.get(
    "apispec",
    "server",
    fallback="http://localhost:5000/"
)
APISPEC_SERVER_DESC = _config.get(
    "apispec",
    "server_desc",
    fallback="Dev 3divi_backend_video_processing API server"
)

# kafka
KAFKA_BROKER = _config.get(
    "kafka",
    "broker",
    fallback="kafka:9092"
)
VIDEO_UPLOAD_TOPIC = _config.get(
    "kafka",
    "video_upload_topic",
    fallback="video_upload_topic"
)
FACE_RECOGNITION_TOPIC = _config.get(
    "kafka",
    "face_recognition_topic",
    fallback="face_recognition_topic"
)
