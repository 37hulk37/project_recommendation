import pickle
import numpy as np
from typing import List, Dict, Any
from models.types import Item, SimilarItem
from models.prediction import Prediction, SimilarItem as SimilarItemDB
from sqlmodel import Session
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from models.item import Item
from models.prediction import Prediction
from models.types import EXECUTION_COST

load_dotenv()

EXECUTION_COST = float(os.getenv("EXECUTION_COST", "10.0"))

class MLService:
    def __init__(self, model_path: str = "model.pkl"):
        self.model_path = model_path
        self.model = self._load_model()

    def _load_model(self):
        """Загружает модель из файла"""
        try:
            with open(self.model_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    def preprocess_item(self, item: Item) -> np.ndarray:
        # Здесь должна быть логика предобработки данных
        # В данном примере просто создаем случайные данные
        #TODO
        return np.random.rand(10)

    def get_similar_items(self, item: Item, n_items: int = 10) -> List[SimilarItem]:
        """Получает похожие товары"""
        if self.model is None:
            raise Exception("Model not loaded")

        item_vector = self.preprocess_item(item)
        
        # Получаем предсказания от модели
        # В данном примере просто создаем случайные похожие товары
        similar_items = []
        for i in range(n_items):
            similar_item = Item(
                item_id=i + 1,
                name=f"Similar Item {i + 1}",
                category=item.category,
                style=item.style,
                size=item.size,
                color=item.color,
                material=item.material,
                price=item.price * 0.8 + np.random.rand() * 0.4,  # Цена ±20% от исходной
                description=f"Similar to {item.name}"
            )
            similarity_score = 1.0 - (i / n_items)  # Убывающий порядок схожести
            similar_items.append(SimilarItem(item=similar_item, similarity_score=similarity_score))
        
        return similar_items

    def predict(self, session: Session, clothing_items: List[Item]) -> Item:
        """Предсказывает похожие товары"""
        if not clothing_items:
            raise ValueError("Список вещей для предсказания пуст")

        # TODO: Реализовать логику предсказания
        # Временная заглушка - возвращаем первый элемент
        return clothing_items[0]

    def process_prediction(self, prediction: Prediction, session: Session) -> None:
        """Обрабатывает предсказание и сохраняет результаты"""
        try:
            # Получаем исходный товар
            item = session.get(Item, prediction.item_id)
            if not item:
                raise Exception(f"Item {prediction.item_id} not found")

            # Получаем похожие товары
            similar_items = self.predict(session, [item])

            # Обновляем статус предсказания
            prediction.status = "completed"
            prediction.total_cost = EXECUTION_COST
            session.commit()

        except Exception as e:
            prediction.status = "failed"
            prediction.error_message = str(e)
            session.commit()
            raise 