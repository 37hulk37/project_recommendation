from sqlalchemy import Column, Integer, Float

from app.database.database import Base

class Account(Base):
    __tablename__ = "account"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, nullable=False, default=0.0)

    def deduct_balance(self, session, amount: float):
        if self.balance >= amount:
            self.balance -= amount
            session.add(self)
            session.commit()
            session.refresh(self)
        else:
            raise ValueError("Недостаточно средств на балансе")

    def add_balance(self, session, amount: float):
        if amount > 0:
            self.balance += amount
            session.add(self)
            session.commit()
            session.refresh(self)
        else:
            raise ValueError("Сумма пополнения должна быть положительной")