from flask import Blueprint

from libs.transport.consumer.kafka_consumers import VideoUploadConsumer

from settings import KAFKA_BROKER, VIDEO_UPLOAD_TOPIC


bp = Blueprint("video_upload_consumer", __name__)


@bp.cli.command("run", help="listening messages from kafka")
def run():
    """
    Starts consuming messages from kafka.
    Returns:
        None:
    """
    # @@@
    consumer = VideoUploadConsumer(
        VIDEO_UPLOAD_TOPIC,
        group_id="video_upload_group",
        broker=KAFKA_BROKER,
    )
    consumer.activate_listener()
