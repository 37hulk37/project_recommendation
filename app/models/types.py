from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

EXECUTION_COST = 10.0


class Category(Enum):
    T_SHIRT = "T-shirt"
    JEANS = "Jeans"
    DRESS = "Dress"
    SUIT = "Suit"
    SKIRT = "Skirt"
    TROUSERS = "Trousers"
    BOOTS = "Boots"
    SNEAKERS = "Sneakers"
    SHOES = "Shoes"


class ClothingStyle(Enum):
    SPORTY = "Sporty "
    CASUAL = "Casual"
    CLASSIC = "Classic"
    STREETWEAR = "Streetwear"
    PUNK = "Punk"


class Size(Enum):
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"
    XXL = "XXL"


class Color(Enum):
    RED = "Red"
    GREEN = "Green"
    BLUE = "Blue"
    YELLOW = "Yellow"
    CYAN = "Cyan"
    MAGENTA = "Magenta"
    BLACK = "Black"
    WHITE = "White"
    GRAY = "Gray"
    ORANGE = "Orange"
    PURPLE = "Purple"
    BROWN = "Brown"
    PINK = "Pink"


class Material(Enum):
    COTTON = "Cottom"
    LINEN = "Linen"
    WOOL = "Wool"
    SILK = "Silk"
    POLYESTER = "Polyester"
    NYLON = "Nylon"
    LEATHER = "Leather"
    SUEDE = "Suede"
    DENIM = "Denim"


class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    male: bool


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    male: bool

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        from_attributes = True


class AccountResponse(BaseModel):
    id: int
    balance: float

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        from_attributes = True


class Item(BaseModel):
    item_id: int
    name: str
    category: Category
    style: ClothingStyle
    size: Size
    color: Color
    material: Material
    price: float
    description: str


class ItemCreate(BaseModel):
    name: str
    category: Category
    style: ClothingStyle
    size: Size
    color: Color
    material: Material
    price: float
    description: str


class ItemResponse(BaseModel):
    item_id: int
    name: str
    category: Category
    style: ClothingStyle
    size: Size
    color: Color
    material: Material
    price: float
    description: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        from_attributes = True


class SimilarItem(BaseModel):
    item: ItemResponse
    similarity_score: float


class PredictionRequest(BaseModel):
    item_id: int


class PredictionResponse(BaseModel):
    prediction_id: int
    created_at: datetime
    similar_items: List[SimilarItem]
    status: str  # "pending", "processing", "completed", "failed"
    error_message: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
