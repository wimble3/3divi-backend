import http

from app.api.helpers.helpers import send_kafka_message
from app.api.helpers.schemas import BinaryResponseSchema
from app.api.videos.helpers import form_kafka_message_to_upload, save_file

from flask import Blueprint, request

from settings import ALLOWED_VIDEO_EXTENSIONS, VIDEO_UPLOAD_TOPIC


bp = Blueprint("api_products", __name__, url_prefix="/api/videos")


@bp.route("/upload", methods=["POST"])
def upload_video():
    """
    Get a list of products by filters.

    Returns:
        JSON object with success or error message from server
    ---
    post:
        summary: Upload file.
        requestBody:
            required: true
            content:
                multipart/form-data:
                    schema:
                        type: object
                        properties:
                            file:
                                type: string
                                format: binary
        responses:
            '200':
                description: Success
                content:
                    application/json:
                        schema:
                            type: integer
                        example: 6889735465
            '400':
                description: Bad request
                content:
                    application/json:
                        schema:
                            type: integer
                        example: 6889735465
        tags:
            - Videos
    """
    file = request.files.get("file")
    if file:
        file_extension = file.filename.split(".")[-1]
        if file_extension in ALLOWED_VIDEO_EXTENSIONS:
            message = form_kafka_message_to_upload(file_extension)
            save_file(
                file, message.get("filepath"))
            send_kafka_message(VIDEO_UPLOAD_TOPIC, message)

            return BinaryResponseSchema().dump(
                {"message": "Video is uploading", "result": True}
            ), http.HTTPStatus.OK

        return BinaryResponseSchema().dump(
            {"message": f"Video has not been upload, allowed video extensions:"
                        f" {ALLOWED_VIDEO_EXTENSIONS}", "result": True}
        ), http.HTTPStatus.OK

    return BinaryResponseSchema().dump(
        {"message": "Video has not been upload", "result": False}
    ), http.HTTPStatus.BAD_REQUEST
