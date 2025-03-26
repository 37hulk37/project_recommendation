import time

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError, IntegrityError
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
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # Если таблицы уже существуют, не пытаемся их пересоздать
    if existing_tables:
        return
        
    try:
        # Создаем все таблицы
        Base.metadata.create_all(engine)
    except IntegrityError as e:
        # Если возникла ошибка уникальности, игнорируем её
        # так как это может означать, что таблицы уже созданы другим процессом
        pass
