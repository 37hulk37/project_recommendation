import json
import pika
from typing import Dict, Any
import os
from database.database import init_db, get_session
from services.queue_service import QueueService
from services.ml_service import MLService
from models.prediction import Prediction

def process_task(ch, method, properties, body):
    try:
        #Получаем данные задачи
        task_data = json.loads(body)
        prediction_id = task_data.get("prediction_id")
        
        if not prediction_id:
            print("Error: prediction_id not found in task data")
            return

        session = next(get_session())
        ml_service = MLService()

        # Получаем предсказание из базы
        prediction = session.get(Prediction, prediction_id)
        if not prediction:
            print(f"Error: prediction {prediction_id} not found")
            return

        # Обрабатываем предсказание
        ml_service.process_prediction(prediction, session)
        print(f"Successfully processed prediction {prediction_id}")

    except Exception as e:
        print(f"Error processing task: {e}")
        if prediction:
            prediction.status = "failed"
            prediction.error_message = str(e)
            session.commit()

    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

def main():

    init_db()

    #Сервис для работы с очередью
    queue_service = QueueService()

    try:
        print("Worker started. Waiting for tasks...")
        queue_service.start_consuming(process_task)
    except KeyboardInterrupt:
        print("Worker stopped by user")
    finally:
        queue_service.close()

if __name__ == "__main__":
    main()