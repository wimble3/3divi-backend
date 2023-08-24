import base64
import json

from werkzeug.datastructures import FileStorage


def serialize(obj):
    """
    Custom serializer for correct FileStorage data sending to kafka.
    Args:
        obj (Any): object to serializing

    Returns:
        str: serialized data
    """
    if isinstance(obj, FileStorage):
        file_data = obj.read()
        serialized_data = base64.b64encode(file_data).decode("utf-8")
        return serialized_data
    return json.dumps(obj).encode("utf-8")
