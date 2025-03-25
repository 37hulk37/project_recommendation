import time

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import get_settings

Base = declarative_base()

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
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    with SessionLocal() as session:
        yield session

def init_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
