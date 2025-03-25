from sqlmodel import SQLModel, Field, Relationship
from passlib.context import CryptContext
from typing import Optional, List

from app.models.prediction import Prediction
from .account import Account

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)
    male: bool
    password_hash: str

    account: Optional[Account] = Relationship(back_populates="user")
    predictions: List["Prediction"] = Relationship(back_populates="user")

    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)