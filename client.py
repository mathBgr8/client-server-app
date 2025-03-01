import streamlit as st
from server import *


if "user" not in st.session_state:
    st.session_state["user"] = None
    st.session_state["role"] = None

if "auth_page" not in st.session_state:
    st.session_state["auth_page"] = "Авторизация"

if not st.session_state["user"]:
    selected_page = st.session_state["auth_page"]
else:
    menu = ["Главная.профиль", "Заказы на бирже", "Разместить заказ", "Мои заказы"]
    if st.session_state["role"] == "admin":
        menu.append("Страница администратора")
    selected_page = st.sidebar.selectbox("Меню", menu)

def login_page():
    st.title("Авторизация")
    email = st.text_input("Никнейм")
    password = st.text_input("Пароль", type="password")
    if st.button("Войти"):
        user_data = authenticate_user(email, password)
        if user_data:
            st.session_state["user_id"] = user_data["user_id"]
            st.session_state["user"] = email
            st.session_state["role"] = user_data["role"]
            st.success("Успешная авторизация!")
            st.session_state["auth_page"] = None
            st.rerun()
        else:
            st.error("Неверные данные.")
    if st.button("Регистрация"):
        st.session_state["auth_page"] = "Регистрация"
        st.rerun()

def register_page():
    st.title("Регистрация")
    email = st.text_input("Никнейм")
    password = st.text_input("Пароль", type="password")
    if st.button("Зарегистрироваться"):
        if register_user(email, password):
            st.success("Регистрация успешна!")
            st.session_state["auth_page"] = "Авторизация"
            st.rerun()
        else:
            st.error("Ошибка регистрации.")
    if st.button("Назад к авторизации"):
        st.session_state["auth_page"] = "Авторизация"
        st.rerun()


def user_profile():
    st.title("Мой профиль")

    st.write(f"Авторизован как {st.session_state['user']}")

    if st.button("Выйти"):
        st.session_state["user"] = None
        st.session_state["role"] = None
        st.session_state["auth_page"] = "Авторизация"
        st.rerun()

    st.write("Спасибо, что выбрали нас!")


def all_tasks():
    st.title("Заказы на бирже")
    for task in get_all_tasks():
        with st.expander(f"{task[1]}"):
            st.write(f"{task[2]}")
            st.write(f"Создал пользователь {task[3]}")
            bid = st.text_input("Предложите сумму", key=f"b{task[0]}")
            if st.button("Откликнуться", task[0]):
                add_bid(task[0], st.session_state["user_id"], bid)
                st.success('Отклик получен')

def post_task():
    st.title("Создать заказ")
    task_name=st.text_input("Название заказа")
    task_text=st.text_input("Описание заказа")
    if st.button("Создать"):
        result=add_task(task_name,task_text,st.session_state["user_id"])
        add_client(st.session_state["user_id"],result[0])
        st.success('Заказ создан')

def my_orders():
    st.title("Мои заказы")
    for task in get_specific_orders(st.session_state["user_id"]):
        with st.expander(f"{task[1]}"):
            st.write(f"{task[2]}")
            if get_bids_for_task(task[0]):
                for bid in get_bids_for_task(task[0]):
                    if st.button(f"Пользователь {bid[5]} предлагает {bid[3]}", bid[0]):
                        update_bid(bid[0], 'working')
                        add_exec(bid[2],bid[1])
                        st.success('Выбран исполнитель')
            else:
                st.write("Откликов нет")
    st.title("Мои задачи")
    for task in get_my_tasks(st.session_state["user_id"]):
        with st.expander(f"{task[1]}"):
            st.write(f"{task[2]}")
            st.write(f"От заказчика{get_user(task[3])[0]}")


if selected_page == "Авторизация":
    login_page()
elif selected_page == "Регистрация":
    register_page()
elif selected_page == "Главная.профиль":
    user_profile()
elif selected_page == "Заказы на бирже":
    all_tasks()
elif selected_page == "Разместить заказ":
    post_task()
elif selected_page == "Мои заказы":
    my_orders()
