from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlmodel import Session

from .item import Item
from .types import EXECUTION_COST, PredictionRequest
from ..database.database import Base
from ..services.crud.account import get_account_by_user_id, update_account_balance
from ..services.crud.user import get_user_by_id


class MLModel(Base):
    __tablename__ = "mlmodel"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # Отношения
    ml_tasks = relationship("MLTask", back_populates="model")

    def predict(self, session: Session, clothing_items: List[Item]) -> Item:
        if not clothing_items:
            raise ValueError("Список вещей для предсказания пуст")

        # TODO: Реализовать логику предсказания
        # Временная заглушка - возвращаем первый элемент
        return clothing_items[0]

    def execute(self, session: Session, user_id: int) -> Item:
        user = get_user_by_id(session, user_id)
        user_account = get_account_by_user_id(session, user_id)

        if not user or not user_account:
            raise ValueError("Пользователь или аккаунт не найден")

        try:
            if user_account.balance >= EXECUTION_COST:
                updated_account = update_account_balance(
                    session=session,
                    account=user_account,
                    new_balance=user_account.balance - EXECUTION_COST
                )

                request = session.get(PredictionRequest, self.request_id)
                if not request:
                    raise ValueError("Запрос на предсказание не найден")

                predicted_item = self.model.predict(
                    session=session,
                    clothing_items=request.clothing_items
                )

                # TODO: Реализовать сохранение истории предсказаний
                # history = PredictionHistory(
                #     user_id=self.user_id,
                #     request_id=self.request_id,
                #     predicted_item_id=predicted_item.item_id,
                #     cost=EXECUTION_COST
                # )
                # create_prediction_history(session=session, history=history)

                return predicted_item
            else:
                raise ValueError("Недостаточно средств на балансе")

        except Exception as e:
            session.rollback()
            if user_account:
                update_account_balance(
                    session=session,
                    account=user_account,
                    new_balance=user_account.balance + EXECUTION_COST
                )
            raise e


class MLTask(Base):
    __tablename__ = "ml_task"

    task_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    request_id = Column(Integer, ForeignKey("predictionrequest.request_id"))
    model_id = Column(Integer, ForeignKey("mlmodel.id"))

    # Отношения
    user = relationship("User", back_populates="ml_tasks")
    request = relationship("PredictionRequest", back_populates="ml_tasks")
    model = relationship("MLModel", back_populates="ml_tasks")
