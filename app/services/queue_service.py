import json
import pika
import time
from typing import Callable, Dict, Any
from database.config import get_settings

class QueueService:
    def __init__(self, max_retries=5, retry_delay=5):
        self.connection = None
        self.channel = None
        self.queue_name = "ml_tasks"
        self.settings = get_settings()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connect()

    def connect(self):
        retries = 0
        while retries < self.max_retries:
            try:
                # Получаем параметры подключения из настроек
                credentials = pika.PlainCredentials(
                    self.settings.RABBITMQ_USER,
                    self.settings.RABBITMQ_PASS
                )
                parameters = pika.ConnectionParameters(
                    host=self.settings.RABBITMQ_HOST,
                    port=self.settings.RABBITMQ_PORT,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()

                # Объявляем очередь
                self.channel.queue_declare(queue=self.queue_name, durable=True)
                return
            except pika.exceptions.AMQPConnectionError as e:
                retries += 1
                if retries == self.max_retries:
                    raise e
                print(f"Failed to connect to RabbitMQ. Retrying in {self.retry_delay} seconds... (Attempt {retries}/{self.max_retries})")
                time.sleep(self.retry_delay)

    def publish_task(self, task_data: Dict[str, Any]):
        """Отправляет задачу в очередь"""
        message = json.dumps(task_data)
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Делаем сообщение persistent
                content_type='application/json'
            )
        )

    def start_consuming(self, callback: Callable[[Dict[str, Any]], None]):
        """Начинает прослушивание очереди"""
        self.channel.basic_qos(prefetch_count=1)  # Справедливое распределение задач
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback)
        self.channel.start_consuming()

    def close(self):
        """Закрывает соединение"""
        if self.connection and not self.connection.is_closed:
            self.connection.close() 