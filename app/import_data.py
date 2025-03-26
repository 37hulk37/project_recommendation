import csv
import pandas as pd
from sqlalchemy import create_engine
from models.item import Item
from models.types import Color, Material, ClothingStyle, Size, Category
from database.database import Base, SessionLocal

def import_data_from_csv():
    # Создаем подключение к базе данных
    engine = create_engine('postgresql://myuser:mypassword@database:5432/postgres')
    
    # Создаем таблицы, если они не существуют
    Base.metadata.create_all(bind=engine)
    
    # Читаем CSV файл
    df = pd.read_csv('data-generation.csv')
    
    # Создаем сессию базы данных
    db = SessionLocal()
    
    try:
        # Импортируем каждую строку из CSV
        for _, row in df.iterrows():
            # Преобразуем строковые значения в соответствующие enum
            color = Color(row['color'])
            material = Material(row['material'])
            category = Category(row['category'])
            style = ClothingStyle(row['style'])
            size = Size(row['size'])
            
            # Создаем объект Item
            item = Item(
                name=row['name'],
                description=row['description'],
                color=color,
                material=material,
                category=category,
                price=float(row['price']),
                style=style,
                size=size
            )
            
            # Добавляем в базу данных
            db.add(item)
        
        # Сохраняем изменения
        db.commit()
        print("Данные успешно импортированы в базу данных")
        
    except Exception as e:
        print(f"Произошла ошибка при импорте данных: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_data_from_csv() 