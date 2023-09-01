import logging
import os
import uuid

from sqlalchemy.exc import DatabaseError, DataError
from werkzeug.datastructures import FileStorage  # noqa: F401

from app import after_video_upload_views, redis_service, db
from app.api.helpers.helpers import send_kafka_message
from app.api.videos.models import Video
from libs.face_recognition import FaceRecognitionStatusEnum
from settings import FACE_RECOGNITION_TOPIC


def form_kafka_message_to_upload(file_extension):
    """
    Forms message to kafka with uuid and filepath of file.
    Args:
        file_extension (str): file extension string [example='mkv']
    Returns:
        dict: dict with uuid and filepath
    """
    file_id = str(uuid.uuid4())
    return {
        "file_id": file_id,
        "filepath": f"/app/media/videos/{file_id}.{file_extension}"
    }


def save_file(file, filepath):
    """
    Saves file locally.
    Args:
        file (FileStorage): file
        filepath (str): file path

    Returns:
        str: save path
    """
    save_path = os.path.join(os.getcwd(), filepath)
    file.save(save_path)
    return save_path


@after_video_upload_views
def send_kafka_message_to_face_recognition(file_id, filepath):
    """
    Starts video recognition process.
    Args:
        file_id (str): file id
        filepath (str): filepath

    Returns:

    """
    send_kafka_message(
        FACE_RECOGNITION_TOPIC,
        {
            "filepath": filepath,
            "file_id": file_id
        }
    )


def create_video(file_id, data, status, frame, persons, filepath):
    try:
        video = Video(
            id=file_id,
            data=data,
            status=status,
            frame=frame,
            persons=persons,
            filepath=filepath
        )
        db.session.add(video)
        db.session.commit()
        return True
    except DatabaseError as e:
        logging.error(f"Creation video in db failed: {e}")
        return False
