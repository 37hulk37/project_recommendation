from datetime import datetime

from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime

from database.database import Base


class SimilarItem(Base):
    __tablename__ = "similar_item"
    __table_args__ = {'extend_existing': True}

    similar_item_id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("prediction.prediction_id"), nullable=False)
    item_id = Column(Integer, ForeignKey("item.item_id"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    cost = Column(Float, nullable=False, default=10.0)  # Стоимость предсказания


class Prediction(Base):
    __tablename__ = "prediction"
    __table_args__ = {'extend_existing': True}

    prediction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("item.item_id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String, nullable=False, default="pending")  # pending, processing, completed, failed
    error_message = Column(String, nullable=True)
    total_cost = Column(Float, nullable=False, default=10.0)  # Общая стоимость предсказания