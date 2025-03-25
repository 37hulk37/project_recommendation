from item import Item
from prediction import PredictionHistory
from .types import EXECUTION_COST
from ..services.crud.account import get_account_by_user_id, update_account_balance
from ..services.crud.prediction import create_prediction_history
from ..services.crud.user import get_user_by_id

from sqlmodel import SQLModel, Field, Relationship, Session
from typing import Optional, List
from .prediction import PredictionRequest


class MLModel(SQLModel, table=True):
    model_id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    def predict(self, session: Session, clothing_items: List[Item]) -> Item:
        if not clothing_items:
            raise ValueError("Список вещей для предсказания пуст")

        # TODO: Реализовать логику предсказания
        # Временная заглушка - возвращаем первый элемент
        return clothing_items[0]

    def execute(self, session: Session) -> Item:
        user = get_user_by_id(session, self.user_id)
        user_account = get_account_by_user_id(session, self.user_id)

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

                history = PredictionHistory(
                    user_id=self.user_id,
                    request_id=self.request_id,
                    predicted_item_id=predicted_item.item_id,
                    cost=EXECUTION_COST
                )
                create_prediction_history(session=session, history=history)

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


class MLTask(SQLModel, table=True):
    task_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id")
    request_id: int = Field(foreign_key="predictionrequest.request_id")
    model_id: int = Field(foreign_key="mlmodel.model_id")

    user: Optional["User"] = Relationship()
    request: Optional[PredictionRequest] = Relationship()
    model: Optional[MLModel] = Relationship()
