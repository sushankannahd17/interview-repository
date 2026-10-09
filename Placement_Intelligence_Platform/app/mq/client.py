import pika

from app.core.config import settings


# Open a fresh RabbitMQ connection and channel with the work queue declared
def get_channel():
    # Parse the AMQP URL into connection parameters
    parameters = pika.URLParameters(settings.amqp_url)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    dead_letter_queue = f"{settings.amqp_queue}.dead"
    channel.queue_declare(queue=dead_letter_queue, durable=True)
    channel.queue_declare(
        queue=settings.amqp_queue,
        durable=True,
        arguments={
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": dead_letter_queue,
        },
    )
    return connection, channel
