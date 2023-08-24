from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from apispec_webframeworks.flask import FlaskPlugin

from app import app

from flask import current_app


from settings import (
    APISPEC_OPENAPI_VER,
    APISPEC_SERVER,
    APISPEC_SERVER_DESC,
    APISPEC_TITLE,
    APISPEC_VERSION,
    SWAGGER_FILENAME,
)


def add_responses(documentation):
    """
    Adding responses to spec.
    Args:
        documentation (FlaskApiSpec): app's documentation

    Returns:
        None:
    """
    response_400 = {
        "description": "Wrong input data format",
        "content": {
            "application/json": {
                "schema": "BinaryResponseSchema",
                "examples": {
                    "Bad Request": {
                        "value": {
                            "message": "Wrong input data format",
                            "result": False,
                        }
                    }
                },
            }
        },
    }
    response_401 = {
        "description": "Authorization error",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "A message from the server",
                        },
                        "result": {"type": "boolean"},
                    },
                },
                "examples": {
                    "Invalid token": {
                        "value": {
                            "message": "The auth token is invalid or "
                                       "its validity period has expired",
                            "result": False,
                        }
                    },
                    "No token": {
                        "value": {
                            "message": "The user is not logged in, "
                                       "auth token is missing",
                            "result": False,
                        }
                    },
                },
            }
        },
    }
    response_403 = {
        "description": "You do not have permission to authorize",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "A message from the server",
                        },
                        "result": {"type": "boolean"},
                    },
                },
                "examples": {
                    "Not enough rights": {
                        "value": {
                            "message": "Not enough rights to give out a "
                                       "given role",
                            "result": False,
                        }
                    },
                    "The session was closed": {
                        "value": {
                            "message": "The session is not active",
                            "result": False,
                        }
                    },
                },
            }
        },
    }
    response_415 = {
        "description": "The input data format is not JSON",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "description": "The input data format is not JSON",
                    "properties": {
                        "message": {"type": "string"},
                        "result": {"type": "boolean"},
                    },
                },
                "examples": {
                    "No JSON": {
                        "value": {
                            "message": "The input data format is not JSON",
                            "result": False,
                        }
                    }
                },
            }
        },
    }
    response_404 = {
        "description": "The requested resource was not found",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "description": "The requested resource was not found",
                    "properties": {
                        "message": {"type": "string"},
                        "result": {"type": "boolean"},
                    },
                },
                "examples": {
                    "Not found": {
                        "value": {
                            "message": "The requested resource was not found",
                            "result": False,
                        },
                    },
                },
            },
        },
    }

    documentation.components.response("BadRequest", response_400)
    documentation.components.response("Unauthorized", response_401)
    documentation.components.response("NoJson", response_415)
    documentation.components.response("Forbidden", response_403)
    documentation.components.response("NotFound", response_404)


def add_view_to_docs(documentation):
    """
    Adding flask views to api docs.
    Args:
        documentation (FlaskApiSpec): app's documentation

    Returns:
        None:
    """
    for fn_name in app.view_functions:
        if "api" in fn_name and "flask-apispec" not in fn_name:
            view_fn = app.view_functions[fn_name]
            with app.app_context():
                documentation.path(view=view_fn)


def write_docs_to_file(documentation):
    """
    Writing docs to yaml file.
    Args:
        documentation (FlaskApiSpec): app's documentation

    Returns:
        None:
    """
    try:
        file = open(SWAGGER_FILENAME, "w")
        with app.app_context():
            print(documentation.to_yaml(), file=file)
        file.close()
    except PermissionError:
        current_app.logger.info(
            f"No right to create file {SWAGGER_FILENAME}."
        )


def create_spec():
    """
    Creates docs and saves to yaml file.

    Returns:
        None:
    """
    apispec = APISpec(
        title=APISPEC_TITLE,
        version=APISPEC_VERSION,
        plugins=[MarshmallowPlugin(), FlaskPlugin()],
        openapi_version=APISPEC_OPENAPI_VER,
        servers=[{"url": APISPEC_SERVER, "description": APISPEC_SERVER_DESC}],
    )

    add_responses(apispec)
    add_view_to_docs(apispec)
    write_docs_to_file(apispec)
    return apispec


if __name__ == "__main__":
    create_spec()
