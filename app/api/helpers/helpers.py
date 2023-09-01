import os

import boto3

from libs.transport.publisher.kafka_publisher import KafkaPublisher

from werkzeug.datastructures import FileStorage  # noqa: F401


def send_kafka_message(topic, message):
    """
    Sends message to kafka service.
    Args:
        topic (str): kafka topic
        message (dict): message with information about file.

    Returns:
        None:
    """
    publisher = KafkaPublisher()
    publisher.send_message(topic, **message)


def upload_file_to_s3(filepath, bucket, filename):
    """
    Uploads file to s3 service.
    Args:
        filename (str): filename
        filepath (str): filepath
        bucket (str): bucket name

    Returns:
        tuple:
    """
    s3_client = boto3.client(
        "s3",
        endpoint_url="http://s3:9000",
        aws_access_key_id="access-key",
        aws_secret_access_key="secret-key"
    )

    s3_client.upload_file(filepath, bucket, filename)

    return filepath, bucket, filename


def delete_file(file_path):
    """
    Deletes file locally.
    Args:
        file_path (str): file path

    Returns:
        None:
    """
    os.remove(file_path)
