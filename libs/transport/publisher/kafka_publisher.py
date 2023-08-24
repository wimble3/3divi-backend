import json

from kafka import KafkaProducer


class KafkaPublisher:
    def __init__(self):
        self.producer = None
        self.connect()

    def send_message(self, topic, **kwargs):
        if self.producer:
            future = self.producer.send(topic, kwargs)
            future.get(timeout=60)
            self.producer.flush()
        else:
            self.connect()

    def connect(self):
        self.producer = KafkaProducer(
            bootstrap_servers="kafka:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks=0,
            retries=3,
            api_version=(2, 1, 0)
        )

    def _reconnect(self):
        if self.producer:
            self.producer.close()
            self.producer = None
        self.connect()

    def close(self):
        if self.producer:
            self.producer.close()
            self.producer = None
