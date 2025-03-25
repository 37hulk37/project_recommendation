from sqlalchemy import Column, Integer, String, Float, Enum

from models.types import Color, Material, ClothingStyle, Size, Category
from database.database import Base


class Item(Base):
    __tablename__ = "item"
    __table_args__ = {'extend_existing': True}

    item_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    color = Column(Enum(Color), nullable=True)
    material = Column(Enum(Material), nullable=True)
    category = Column(Enum(Category), nullable=True)
    price = Column(Float, nullable=False)
    style = Column(Enum(ClothingStyle), nullable=True)
    size = Column(Enum(Size), nullable=True)
