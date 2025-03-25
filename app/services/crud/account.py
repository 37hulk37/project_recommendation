from typing import Optional
from sqlmodel import Session

from models.account import Account


def get_account_by_user_id(session: Session, user_id: int) -> Optional[Account]:
    return session.query(Account).filter(Account.id == user_id).first()


def update_account_balance(session: Session, account: Account, new_balance: float) -> Account:
    if new_balance >= 0:
        account.balance = new_balance
        session.add(account)
        session.commit()
        session.refresh(account)
    else:
        raise ValueError("Баланс не может быть отрицательным")
    return account


def delete_account(session: Session, account: Account) -> None:
    session.delete(account)
    session.commit()


