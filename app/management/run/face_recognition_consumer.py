from flask import Blueprint

from libs.transport.consumer.kafka_consumers import VideoUploadConsumer

from settings import FACE_RECOGNITION_TOPIC, KAFKA_BROKER

bp = Blueprint("face_recognition_consumer", __name__)


@bp.cli.command("run", help="listening messages from kafka")
def run():
    """
    Starts consuming messages from kafka.
    Returns:
        None:
    """
    consumer = VideoUploadConsumer(
        FACE_RECOGNITION_TOPIC,
        broker=KAFKA_BROKER,
    )
    consumer.activate_listener()
