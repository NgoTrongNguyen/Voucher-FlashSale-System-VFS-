from kafka import KafkaProducer
from kafka.errors import KafkaError
from typing import Any, Dict
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class KafkaClient:
    def __init__(self):
        # Init Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
            value_serializer = lambda v: json.dumps(v).encode('utf-8'),
            acks = 'all',
            retries = 3,
        )