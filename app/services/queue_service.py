import json
import pika
from typing import Callable, Dict, Any
import os

class QueueService:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = "ml_tasks"
        self.connect()

    def connect(self):
        # Получаем параметры подключения из переменных окружения
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
        rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
        rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
        rabbitmq_pass = os.getenv("RABBITMQ_PASS", "guest")

        # Создаем подключение
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
        parameters = pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        # Объявляем очередь
        self.channel.queue_declare(queue=self.queue_name, durable=True)

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