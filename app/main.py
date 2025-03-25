from fastapi import FastAPI, Depends, HTTPException, status
import os
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database.database import init_db, get_session
from models.item import Item as ItemDB
from models.prediction import Prediction
from models.types import (
    UserCreate, UserResponse, AccountResponse,
    PredictionRequest, Token, ItemCreate, ItemResponse,
    PredictionResponse, EXECUTION_COST
)
from services.crud.account import get_account_by_user_id, update_account_balance
from services.crud.user import register_user, get_user_by_email
from services.queue_service import QueueService

app = FastAPI(title="Fashion Recommendation Service")
security = HTTPBasic()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Настройки JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Инициализация сервисов
queue_service = QueueService()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_email(session, email)
    if user is None:
        raise credentials_exception
    return user

@app.on_event("startup")
async def startup_event():
    init_db()
    # Создаем демо пользователя при запуске
    session = next(get_session())
    demo_email = "demo@example.com"
    if not get_user_by_email(session, demo_email):
        demo_user = UserCreate(
            email=demo_email,
            password="demo123",
            name="Demo User",
            male=True
        )
        register_user(session=session, **demo_user.model_dump())

# Эндпоинты аутентификации
@app.post("/register", response_model=UserResponse)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = get_user_by_email(session, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_dict = user.dict()
    user_dict["password"] = get_password_hash(user_dict["password"])
    return register_user(session=session, **user_dict)

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = get_user_by_email(session, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Эндпоинты для работы с аккаунтом
@app.get("/account", response_model=AccountResponse)
def get_account(current_user = Depends(get_current_user), session: Session = Depends(get_session)):
    account = get_account_by_user_id(session, current_user.user_id)
    return account

@app.post("/account/deposit")
def deposit_money(amount: float, current_user = Depends(get_current_user), session: Session = Depends(get_session)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    account = get_account_by_user_id(session, current_user.user_id)
    update_account_balance(session, account, account.balance + amount)
    return {"message": "Deposit successful", "new_balance": account.balance + amount}

# Эндпоинты для работы с товарами
@app.post("/items", response_model=ItemResponse)
def create_item(item: ItemCreate, session: Session = Depends(get_session)):
    db_item = ItemDB(**item.dict())
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(ItemDB, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/items", response_model=List[ItemResponse])
def get_items(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    items = session.query(ItemDB).offset(skip).limit(limit).all()
    return items

# Эндпоинты для работы с предсказаниями
@app.post("/prediction", response_model=PredictionResponse)
def create_prediction(
    request: PredictionRequest,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Проверяем баланс пользователя
    account = get_account_by_user_id(session, current_user.user_id)
    if account.balance < EXECUTION_COST:
        raise HTTPException(status_code=402, detail="Insufficient funds")
    
    # Проверяем существование товара
    item = session.get(ItemDB, request.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Создаем предсказание
    prediction = Prediction(
        user_id=current_user.user_id,
        item_id=request.item_id,
        status="pending"
    )
    session.add(prediction)
    session.commit()
    session.refresh(prediction)
    
    # Списываем средства
    update_account_balance(session, account, account.balance - EXECUTION_COST)
    
    # Отправляем задачу в очередь
    queue_service.publish_task({
        "prediction_id": prediction.prediction_id
    })
    
    return prediction

@app.get("/prediction/{prediction_id}", response_model=PredictionResponse)
def get_prediction(
    prediction_id: int,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    prediction = session.get(Prediction, prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    # Проверяем, что предсказание принадлежит пользователю
    if prediction.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return prediction

@app.get("/prediction", response_model=List[PredictionResponse])
def get_predictions(
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    predictions = session.query(Prediction).filter(
        Prediction.user_id == current_user.user_id
    ).all()
    return predictions

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
