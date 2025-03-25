from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from sqlmodel import Session


class Account(SQLModel, table=True):
    account_id: Optional[int] = Field(default=None, primary_key=True)
    balance: float = Field(default=0.0)
    user_id: int = Field(foreign_key="user.user_id")

    user: Optional["User"] = Relationship(back_populates="account")

    def deduct_balance(self, session: Session, amount: float):
        if self.balance >= amount:
            self.balance -= amount
            session.add(self)
            session.commit()
            session.refresh(self)
        else:
            raise ValueError("Недостаточно средств на балансе")

    def add_balance(self, session: Session, amount: float):
        if amount > 0:
            self.balance += amount
            session.add(self)
            session.commit()
            session.refresh(self)
        else:
            raise ValueError("Сумма пополнения должна быть положительной")