from typing import List, Optional
from sqlmodel import Session

from models.account import Account
from models.user import User


def get_all_users(session: Session) -> List[User]:
    return session.query(User).all()

def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    return session.query(User).filter(User.email == email).first()

def update_user(session: Session, user_id: int, update_data: dict) -> Optional[User]:
    user = session.get(User, user_id)
    if user:
        for key, value in update_data.items():
            setattr(user, key, value)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

def delete_user(session: Session, user_id: int) -> None:
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()

def register_user(session: Session, name: str, email: str, male: bool, password: str) -> User:
    # Создаем пользователя
    user = User(name=name, email=email, male=male)
    user.set_password(password)
    
    # Сохраняем пользователя для получения user_id
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Создаем аккаунт для пользователя
    account = Account(id=user.id, balance=0.0)
    session.add(account)
    session.commit()
    
    return user