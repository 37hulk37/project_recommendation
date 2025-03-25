from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from .user import User
from .item import Item


class SimilarItem(SQLModel, table=True):
    similar_item_id: Optional[int] = Field(default=None, primary_key=True)
    prediction_id: int = Field(foreign_key="prediction.prediction_id")
    item_id: int = Field(foreign_key="item.item_id")
    similarity_score: float
    cost: float = Field(default=10.0)  # Стоимость предсказания

    prediction: "Prediction" = Relationship(back_populates="similar_items")
    item: Item = Relationship(back_populates="similar_items")


class Prediction(SQLModel, table=True):
    prediction_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id")
    item_id: int = Field(foreign_key="item.item_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, processing, completed, failed
    error_message: Optional[str] = None
    total_cost: float = Field(default=10.0)  # Общая стоимость предсказания
    
    user: User = Relationship(back_populates="predictions")
    item: Item = Relationship(back_populates="predictions")
    similar_items: List[SimilarItem] = Relationship(back_populates="prediction")