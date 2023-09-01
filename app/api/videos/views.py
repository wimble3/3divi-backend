import http
import logging

from app import redis_service
from app.api.helpers.helpers import send_kafka_message
from app.api.helpers.schemas import BinaryResponseSchema
from app.api.videos.helpers import form_kafka_message_to_upload, save_file, \
    create_video

from flask import Blueprint, request

from app.api.videos.models import Video
from app.api.videos.schemas import VideoSchema, VideoResponseSchema
from libs.face_recognition import FaceRecognitionStatusEnum
from settings import ALLOWED_VIDEO_EXTENSIONS, VIDEO_UPLOAD_TOPIC, REDIS_DB, \
    REDIS_PORT, REDIS_HOST, FACE_RECOGNITION_TOPIC

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
                        f" {ALLOWED_VIDEO_EXTENSIONS}", "result": False}
        ), http.HTTPStatus.BAD_REQUEST

    return BinaryResponseSchema().dump(
        {"message": "Video has not been upload", "result": False}
    ), http.HTTPStatus.BAD_REQUEST


@bp.route("/", methods=["GET"])
def get_status():
    """
    Get file data by file id.

    Returns:
        JSON object with success or error message from server
    ---
    get:
        summary: Get file data by file id.
        parameters:
            - in: query
              name: file_id
              schema:
                type: string
              required: true
              description: The ID of the file to retrieve data for.
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
    file_id = request.args.get("file_id")
    video = Video.query.get(file_id)

    if video:
        return VideoResponseSchema().dump(
            {
                "message": "Video has been retrieved successfuly",
                "video": VideoSchema().dump(video),
                "result": True
            }
        ), http.HTTPStatus.OK

    return BinaryResponseSchema().dump(
        {
            "message": f"No file with if {file_id}",
            "result": False
        }
    ), http.HTTPStatus.BAD_REQUEST


@bp.route("/processing/resume", methods=["GET"])
def processing_resume():
    """
    Resume video processing by file id.

    Returns:
        JSON object with success or error message from server
    ---
    get:
        summary: Resume video processing by file id.
        parameters:
            - in: query
              name: file_id
              schema:
                type: string
              required: true
              description: The ID of the file to retrieve data for.
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
    file_id = request.args.get("file_id")
    data = redis_service.get(file_id)
    resume_status = FaceRecognitionStatusEnum.RESUME
    data["status"] = resume_status
    redis_service.update(file_id, data)

    filepath = data.get("filepath")
    send_kafka_message(
        FACE_RECOGNITION_TOPIC,
        {
            "filepath": filepath,
            "file_id": file_id
        }
    )

    return BinaryResponseSchema().dump(
        {
            "message": f"File with id {file_id} is resuming",
            "result": True
        }
    ), http.HTTPStatus.OK


@bp.route("/processing/pause", methods=["GET"])
def processing_pause():
    """
    Pause video processing by file id.

    Returns:
        JSON object with success or error message from server
    ---
    get:
        summary: Pause video processing by file id.
        parameters:
            - in: query
              name: file_id
              schema:
                type: string
              required: true
              description: The ID of the file to retrieve data for.
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
    file_id = request.args.get("file_id")
    data = redis_service.get(file_id)
    logging.info(data)
    pause_status = str(FaceRecognitionStatusEnum.PAUSE)
    data["faces_list"] = data["faces_list"].tolist()
    data["names_list"] = data["names_list"].tolist()

    # {
    #     "file_id": self.file_id,
    #     "faces_list": self.faces_list,
    #     "names_list": self.names_list,
    #     "status": str(self.status),
    #     "frame": f"{str(self.frame_num)}/{str(self.frame_count)}",
    #     "persons": str(self.persons),
    #     "filepath": self.video_path
    # }
    redis_service.update(file_id, data)

    filepath = data.get("filepath")
    send_kafka_message(
        FACE_RECOGNITION_TOPIC,
        {
            "filepath": filepath,
            "file_id": file_id
        }
    )

    return BinaryResponseSchema().dump(
        {
            "message": f"Processing file with id {file_id} on pause",
            "result": True
        }
    ), http.HTTPStatus.OK
