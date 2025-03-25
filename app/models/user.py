from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String, Boolean

from app.database.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    male = Column(Boolean, nullable=False)
    password = Column(String, nullable=False)

    def set_password(self, password: str):
        self.password = pwd_context.hash(password)

    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)