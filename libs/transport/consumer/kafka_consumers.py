import json
import logging
from concurrent.futures import ThreadPoolExecutor

from app import app
from app.api.events import process_after_video_upload_views

from kafka import KafkaConsumer
from kafka.errors import CommitFailedError

from app.api.videos.helpers import create_video
from libs.face_recognition.face_recognition import FaceRecognition
from settings import KAFKA_BROKER, NUM_MAX_THREADS


# temporary logger for consuming process
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root_logger.addHandler(handler)


class Consumer:
    """Base consumer."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    def __init__(
            self, topic, group_id, broker=KAFKA_BROKER,
            clear_messages=False, threads=8):
        """
        Sets base parameters, checks num of threads.
        Args:
            topic:
            broker:
            clear_messages:
            threads:
        """
        self.consumer = None
        self.topic = topic
        self.broker = broker
        self.group_id = group_id
        self.clear_messages = clear_messages
        self.max_workers = threads

        if threads > NUM_MAX_THREADS:
            logging.warning(f"Sorry, max threads: {NUM_MAX_THREADS}")
            self.max_workers = NUM_MAX_THREADS

        self.pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.connect()

    def activate_listener(self):
        """
        Activates listening process.
        Returns:
            None:
        """
        try:
            self.subscribe_topic()
            for message in self.consumer:
                try:
                    if not self.clear_messages:
                        self.pool.submit(self.process, message)
                    else:
                        logging.info("Ack")
                    self.consumer.commit()
                except Exception as e:
                    logging.error(f"Unexpected error: {e}")
        except CommitFailedError:
            logging.error("Commit error, reconnecting to kafka group")
            self._reconnect()
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    def _reconnect(self):
        """
        Close consumer, connect again and start listening.
        Returns:
            None:
        """
        if self.consumer:
            self.consumer.close()
            self.consumer = None
        self.connect()
        self.activate_listener()

    def stop(self):
        """
        Closes consuming process.
        Returns:
            None:
        """
        self.consumer.close()
        logging.info("Consumer is closed")

    def subscribe_topic(self):
        """
        Subscribes on kafka topic
        Returns:
            None:
        """
        self.consumer.subscribe([self.topic])
        logging.info("Consumer is listening")

    def connect(self):
        """
        Creates KafkaConsumer instance.
        Returns:
            None:
        """
        self.consumer = KafkaConsumer(
            bootstrap_servers=self.broker,
            group_id=self.group_id,
            auto_offset_reset="latest",
            enable_auto_commit=False,
            api_version=(2, 1, 0),
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )

    def process(self, message):
        """
        Processing of consuming.
        Args:
            message (dict): kafka message

        Returns:
            None:
        """
        result = self.on_message(message)
        if result:
            logging.info("ack")
        else:
            logging.info("reject")

    def on_message(self, message):
        """Empty method for child consumers. Using in self.process()"""


class VideoUploadConsumer(Consumer):
    """
    A child consumer to get messages about uploaded videos from kafka.
    Uploads video to s3 service, creates db row.
    """
    def on_message(self, message):
        """
        Uploads video to s3 service, creates db row.
        Args:
            message (dict): message from kafka publisher

        Returns:
            bool: True if file has been uploaded to s3,
                db row has been created else False
        """
        try:
            filepath = message.value.get("filepath")
            file_id = message.value.get("file_id")
            logging.info(f"Uploading video with id: {file_id}")

            process_after_video_upload_views(file_id, filepath)
            return True
        except AssertionError as e:
            logging.error(f"Assertion error: {e}")
            return False


class FaceRecognitionConsumer(Consumer):
    """
    A child consumer to get messages about videos which needed to
    processing of recognition from kafka.
    """
    def on_message(self, message):
        """
        Starts process of recognition.
        Args:
            message (dict): message from kafka publisher

        Returns:
            bool: True if file has been uploaded to s3,
                db row has been created else False
        """
        try:
            filepath = message.value.get("filepath")
            file_id = message.value.get("file_id")
            face_recognition = FaceRecognition(file_id, filepath)
            faces_list, names_list = face_recognition.process()

            data = {"faces_list": faces_list, "names_list": names_list}

            with app.app_context():
                is_video_added = create_video(
                    file_id, data, face_recognition.status,
                    face_recognition.frame_num, face_recognition.persons,
                    filepath
                )
                if not is_video_added:
                    logging.error(
                        f"File with id {file_id} has not been created in db")
                    return False
            logging.info(
                f"File with id {file_id} created in db successfully")
            return True
        except AssertionError as e:
            logging.error(f"Assertion error: {e}")
            return False
