import os
import uuid

from werkzeug.datastructures import FileStorage  # noqa: F401


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
        "id": file_id,
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


def form_kafka_message_to_recognition():
    """"""
