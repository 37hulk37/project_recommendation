from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from .types import Color, Material, ClothingStyle, Size, Category
from sqlalchemy import Column, Enum


class Item(SQLModel, table=True):
    item_id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    color: Color = Field(sa_column=Column(Enum(Color)))
    material: Material = Field(sa_column=Column(Enum(Material)))
    category: Category = Field(sa_column=Column(Enum(Category)))
    price: float
    style: ClothingStyle = Field(sa_column=Column(Enum(ClothingStyle)))
    size: Size = Field(sa_column=Column(Enum(Size)))

    predictions: List["Prediction"] = Relationship(back_populates="item")
    similar_items: List["SimilarItem"] = Relationship(back_populates="item")
