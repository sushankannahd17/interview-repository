import json
import logging

import pika

from app.core.config import settings
from app.mq.client import get_channel

logger = logging.getLogger("mq_producer")


# Publish a single experience_id to the RabbitMQ queue for async processing
def publish_experience_id(experience_id: str) -> bool:
    try:
        connection, channel = get_channel()
        try:
            channel.confirm_delivery()
            message = json.dumps({"experience_id": experience_id}).encode("utf-8")
            confirmed = channel.basic_publish(
                exchange="",
                routing_key=settings.amqp_queue,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2),
                mandatory=True,
            )
        finally:
            connection.close()
        if not confirmed:
            return False
        logger.info("[RABBITMQ] published experience_id=%s", experience_id)
        return True
    except Exception as e:
        logger.error("[RABBITMQ] publish failed experience_id=%s: %s", experience_id, e)
        return False
