from sqlmodel import SQLModel, Session, create_engine
from contextlib import contextmanager
from .config import get_settings
import time
from sqlalchemy.exc import OperationalError

def wait_for_db(retries=5, delay=2):
    for i in range(retries):
        try:
            engine = create_engine(
                url=get_settings().DATABASE_URL_psycopg,
                echo=True,
                pool_size=5,
                max_overflow=10
            )
            # Проверяем подключение
            with engine.connect() as conn:
                return engine
        except OperationalError as e:
            if i == retries - 1:  # Последняя попытка
                raise e
            time.sleep(delay)
    raise Exception("Could not connect to database")

engine = wait_for_db()

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
