import pickle
import numpy as np
import torch
import pandas as pd
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
    def __init__(self, model_path: str = "KNN_model.pth"):
        self.model_path = model_path
        self.model = self._load_model()
        self.df = self._load_data()

    def _load_model(self):
        """Загружает модель из файла"""
        try:
            return torch.load(self.model_path, weights_only=False)
        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    def _load_data(self):
        """Загружает данные для кодирования категорий"""
        try:
            df = pd.read_csv("data-generation.csv")
            # Кодируем категориальные признаки
            for col in ['color', 'material', 'category', 'style', 'size']:
                df[col] = df[col].astype('category').cat.codes
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return None

    def preprocess_item(self, item: Item) -> torch.Tensor:
        """Преобразует товар в тензор для модели"""
        if self.df is None:
            raise Exception("Data not loaded")

        # Создаем словарь с признаками товара
        item_dict = {
            'color': item.color,
            'material': item.material,
            'category': item.category,
            'style': item.style,
            'size': item.size
        }

        # Кодируем признаки
        encoded_features = []
        for feature in ['color', 'material', 'category', 'style', 'size']:
            # Находим код для признака в обучающих данных
            feature_code = self.df[self.df[feature] == item_dict[feature]][feature].iloc[0]
            encoded_features.append(feature_code)

        return torch.tensor(encoded_features, dtype=torch.float32)

    def get_similar_items(self, item: Item, n_items: int = 5) -> List[SimilarItem]:
        """Получает похожие товары"""
        if self.model is None:
            raise Exception("Model not loaded")

        item_vector = self.preprocess_item(item)
        
        # Получаем предсказания от модели
        indices, distances = self.model.recommend(item_vector)
        
        # Преобразуем расстояния в оценки схожести (чем меньше расстояние, тем больше схожесть)
        max_distance = distances[0]
        similar_items = []
        
        for i, idx in enumerate(indices[:n_items]):
            similar_item_data = self.df.iloc[idx]
            similar_item = Item(
                item_id=idx,
                name=f"Similar Item {i + 1}",
                category=similar_item_data['category'],
                style=similar_item_data['style'],
                size=similar_item_data['size'],
                color=similar_item_data['color'],
                material=similar_item_data['material'],
                price=item.price * 0.8 + np.random.rand() * 0.4,  # Цена ±20% от исходной
                description=f"Similar to {item.name}"
            )
            # Преобразуем расстояние в оценку схожести (0-1)
            similarity_score = 1.0 - (distances[i] / max_distance)
            similar_items.append(SimilarItem(item=similar_item, similarity_score=similarity_score))
        
        return similar_items

    def predict(self, session: Session, item: Item) -> List[SimilarItem]:
        """Предсказывает похожие товары"""
        if not item:
            raise ValueError("Товар для предсказания не указан")

        return self.get_similar_items(item)

    def process_prediction(self, prediction: Prediction, session: Session) -> None:
        """Обрабатывает предсказание и сохраняет результаты"""
        try:
            # Получаем исходный товар
            item = session.get(Item, prediction.item_id)
            if not item:
                raise Exception(f"Item {prediction.item_id} not found")

            # Получаем похожие товары
            similar_items = self.predict(session, item)

            # Сохраняем похожие товары в базе данных
            for similar in similar_items:
                similar_item_db = SimilarItemDB(
                    prediction_id=prediction.prediction_id,
                    item_id=similar.item.item_id,
                    similarity_score=similar.similarity_score
                )
                session.add(similar_item_db)

            # Обновляем статус предсказания
            prediction.status = "completed"
            prediction.total_cost = EXECUTION_COST
            session.commit()

        except Exception as e:
            prediction.status = "failed"
            prediction.error_message = str(e)
            session.commit()
            raise 