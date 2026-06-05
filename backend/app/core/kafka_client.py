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

    def send_message(self, topic: str, message: Dict[Any, Any], partition_key: str = None) -> bool:
        """
        Send a message to Kafka topic 
        Args:
            topic: name
            message: dict to send
            partition_key: ordering key
        Returns:
            True if success
        """
        try:
            future = self.producer.send(
                topic,
                value = message,
                key = partition_key.encode('utf-8') if partition_key else None
            )
            future.get(timeout = 10)
            logger.info(f"Sent message to Kafka topic {topic}: {message}")
            return True
        except KafkaError as e:
            logger.error(f"Error sending message to Kafka topic {topic}: {e}")
            return False

    def send_claim_event(self, request_id: str, user_id: int, voucher_id: int, campaign_id: int) -> bool:
        """
        Send a claim message to Kafka
        Args:
            request_id: ID của request
            user_id: ID của user
            voucher_id: ID của voucher
            campaign_id: ID của campaign
        Returns:
            True if success
        """
        message = {
            "request_id": request_id,
            "user_id": user_id,
            "voucher_id": voucher_id,
            "campaign_id": campaign_id,
        }

        # Thay ID bằng partition key
        return self.send_message(
            settings.KAFKA_TOPIC_VOUCHER,
            message,
            partition_key = str(user_id)
        )
        
    # Flush message in producer buffer
    def flush(self):
        self.producer.flush()

    def close(self):
        self.producer.close()
    

kafka_client = KafkaClient()