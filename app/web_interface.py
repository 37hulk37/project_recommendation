import streamlit as st
import requests
import json
from typing import Dict, Optional

API_URL = "http://localhost:8000"

class APIClient:
    def __init__(self):
        self.token: Optional[str] = None
        
    def set_token(self, token: str):
        self.token = token
        
    def get_headers(self) -> Dict:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}
    
    def register(self, name: str, email: str, password: str, male: bool) -> Dict:
        response = requests.post(
            f"{API_URL}/register",
            json={"name": name, "email": email, "password": password, "male": male}
        )
        return response.json()
    
    def login(self, email: str, password: str) -> Dict:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": email, "password": password}
        )
        return response.json()
    
    def get_account(self) -> Dict:
        response = requests.get(f"{API_URL}/account", headers=self.get_headers())
        return response.json()
    
    def deposit(self, amount: float) -> Dict:
        response = requests.post(
            f"{API_URL}/account/deposit",
            params={"amount": amount},
            headers=self.get_headers()
        )
        return response.json()
    
    def get_items(self, skip: int = 0, limit: int = 10) -> Dict:
        response = requests.get(
            f"{API_URL}/items",
            params={"skip": skip, "limit": limit},
            headers=self.get_headers()
        )
        return response.json()
    
    def get_item(self, item_id: int) -> Dict:
        response = requests.get(
            f"{API_URL}/items/{item_id}",
            headers=self.get_headers()
        )
        return response.json()
    
    def create_prediction(self, item_id: int) -> Dict:
        response = requests.post(
            f"{API_URL}/predictions",
            json={"item_id": item_id},
            headers=self.get_headers()
        )
        return response.json()
    
    def get_predictions(self, skip: int = 0, limit: int = 10) -> Dict:
        response = requests.get(
            f"{API_URL}/predictions",
            params={"skip": skip, "limit": limit},
            headers=self.get_headers()
        )
        return response.json()

#Инициализация клиента
api_client = APIClient()

def show_auth_page():
    st.title("Авторизация")
    
    tab1, tab2 = st.tabs(["Вход", "Регистрация"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            submit = st.form_submit_button("Войти")
            
            if submit:
                try:
                    response = api_client.login(email, password)
                    if "access_token" in response:
                        api_client.set_token(response["access_token"])
                        st.session_state.authenticated = True
                        st.success("Успешный вход!")
                        st.rerun()
                    else:
                        st.error("Ошибка входа: Неверные учетные данные")
                except Exception as e:
                    st.error(f"Ошибка входа: {str(e)}")
    
    with tab2:
        with st.form("register_form"):
            name = st.text_input("Имя")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Пароль", type="password", key="reg_password")
            male = st.checkbox("Мужской пол")
            submit = st.form_submit_button("Зарегистрироваться")
            
            if submit:
                try:
                    response = api_client.register(name, email, password, male)
                    if "user_id" in response:
                        st.success("Регистрация успешна! Теперь вы можете войти.")
                    else:
                        st.error("Ошибка регистрации")
                except Exception as e:
                    st.error(f"Ошибка регистрации: {str(e)}")

def show_main_page():
    st.title("Рекомендательная система")
    
    # Сайдбар с балансом и пополнением
    with st.sidebar:
        try:
            account = api_client.get_account()
            st.write(f"Баланс: {account['balance']:.2f} кредитов")
            
            with st.form("deposit_form"):
                amount = st.number_input("Сумма пополнения", min_value=0.0, step=10.0)
                if st.form_submit_button("Пополнить"):
                    response = api_client.deposit(amount)
                    if "balance" in response:
                        st.success(f"Баланс пополнен! Новый баланс: {response['balance']:.2f}")
                    else:
                        st.error("Ошибка пополнения баланса")
        except Exception as e:
            st.error(f"Ошибка получения баланса: {str(e)}")
        
        if st.button("Выйти"):
            st.session_state.authenticated = False
            api_client.set_token(None)
            st.rerun()
    
    # Основной контент
    tab1, tab2, tab3 = st.tabs(["Товары", "Информация о товаре", "История предсказаний"])
    
    with tab1:
        st.subheader("Список товаров")
        try:
            items = api_client.get_items()
            for item in items:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{item['name']}**")
                    st.write(f"Категория: {item['category']}")
                with col2:
                    st.write(f"Цена: {item['price']:.2f}")
                with col3:
                    if st.button("Подробнее", key=f"item_{item['item_id']}"):
                        st.session_state.selected_item_id = item['item_id']
                        st.rerun()
        except Exception as e:
            st.error(f"Ошибка получения списка товаров: {str(e)}")
    
    with tab2:
        if "selected_item_id" in st.session_state:
            try:
                item = api_client.get_item(st.session_state.selected_item_id)
                st.subheader(item['name'])
                st.write(f"Категория: {item['category']}")
                st.write(f"Стиль: {item['style']}")
                st.write(f"Размер: {item['size']}")
                st.write(f"Цвет: {item['color']}")
                st.write(f"Материал: {item['material']}")
                st.write(f"Цена: {item['price']:.2f}")
                st.write(f"Описание: {item['description']}")
                
                if st.button("Получить рекомендации"):
                    try:
                        prediction = api_client.create_prediction(item['item_id'])
                        if "prediction_id" in prediction:
                            st.success("Запрос на рекомендации создан! Проверьте историю предсказаний.")
                        else:
                            st.error("Ошибка создания запроса на рекомендации")
                    except Exception as e:
                        st.error(f"Ошибка получения рекомендаций: {str(e)}")
            except Exception as e:
                st.error(f"Ошибка получения информации о товаре: {str(e)}")
        else:
            st.info("Выберите товар из списка для просмотра подробной информации")
    
    with tab3:
        st.subheader("История предсказаний")
        try:
            predictions = api_client.get_predictions()
            for pred in predictions:
                with st.expander(f"Предсказание #{pred['prediction_id']} - {pred['created_at']}"):
                    st.write(f"Статус: {pred['status']}")
                    st.write(f"Стоимость: {pred['total_cost']:.2f} кредитов")
                    if pred['status'] == 'completed':
                        st.write("Похожие товары:")
                        for similar in pred['similar_items']:
                            st.write(f"- {similar['item']['name']} (схожесть: {similar['similarity_score']:.2%})")
                    elif pred['status'] == 'failed':
                        st.error(f"Ошибка: {pred['error_message']}")
        except Exception as e:
            st.error(f"Ошибка получения истории предсказаний: {str(e)}")

def main():
    st.set_page_config(
        page_title="Рекомендательная система",
        page_icon="🛍️",
        layout="wide"
    )

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    # Отображение соответствующей страницы
    if st.session_state.authenticated:
        show_main_page()
    else:
        show_auth_page()

if __name__ == "__main__":
    main() 