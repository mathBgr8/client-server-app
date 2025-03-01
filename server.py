import psycopg2
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv("./env.env")


def connect_to_db():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return connection
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return None


def register_user(email, password, role="user"):
    connection = connect_to_db()
    if not connection:
        print("Нет соединения с базой данных.")
        return False

    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Users (email, role, hash) VALUES (%s, %s, %s)",
            (email, role, hashed_password)
        )
        connection.commit()
        return True
    except Exception as e:
        print(f"Ошибка регистрации: {e}")
        return False
    finally:
        connection.close()


def authenticate_user(email, password):
    connection = connect_to_db()
    if not connection:
        print("Нет соединения с базой данных.")
        return None

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, hash, role FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        if result:
            user_id, stored_password_hash, role = result
            if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                return {"user_id": user_id, "role": role}
        return None
    except Exception as e:
        print(f"Ошибка авторизации: {e}")
        return None
    finally:
        connection.close()



def add_task(name, text, creator_id):
    connection = connect_to_db()
    if not connection:
        print("Нет соединения с базой данных.")
        return None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
                        INSERT INTO Tasks (task_name, task_text, creator_id)
                        VALUES (%s, %s, %s)
                        """,
            (name, text, creator_id)
        )
        connection.commit()
        cursor.execute(
            """
                        SELECT * FROM Tasks
                        WHERE creator_id= %s
                        """,
            (creator_id,)
        )
        return cursor.fetchone()
    except Exception as e:
        print(f"Ошибка запроса: {e}")
    finally:
        connection.close()

def add_client(user_id, task_id):
    connection = connect_to_db()
    if not connection:
        print("Нет соединения с базой данных.")
        return None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
                        INSERT INTO Clients (client_id, task_id)
                        VALUES (%s, %s)
                        """,
            (user_id, task_id)
        )
        connection.commit()
    except Exception as e:
        print(f"Ошибка запроса: {e}")
    finally:
        connection.close()


def add_exec(user_id, task_id):
    connection = connect_to_db()
    if not connection:
        print("Нет соединения с базой данных.")
        return None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
                        INSERT INTO Execs (exec_id, task_id)
                        VALUES (%s, %s)
                        """,
            (user_id, task_id)
        )
        connection.commit()
    except Exception as e:
        print(f"Ошибка запроса: {e}")
    finally:
        connection.close()


def add_bid(task_id, exec_id, bid_amount, status='not accepted'):
    connection = connect_to_db()
    if not connection:
        print("Нет соединения с базой данных.")
        return None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
                        INSERT INTO Bids (task_id, exec_id, price, status)
                        VALUES (%s, %s, %s, %s)
                        """,
            (task_id, exec_id, bid_amount, status)
        )
        connection.commit()
    except Exception as e:
        print(f"Ошибка запроса: {e}")
    finally:
        connection.close()

def update_bid(bid_id, status):
    connection = connect_to_db()
    if not connection:
        print("Нет соединения с базой данных.")
        return None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
                        UPDATE Bids SET status= %s
                        WHERE bid_id= %s
                        """,
            (status, bid_id)
        )
        connection.commit()
    except Exception as e:
        print(f"Ошибка запроса: {e}")
    finally:
        connection.close()


def get_all_tasks():
    connection = connect_to_db()
    if not connection:
        print("Нет соединения с базой данных.")
        return None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
                        SELECT Tasks.task_id, Tasks.task_name, Tasks.task_text, Users.email FROM Tasks
                        LEFT JOIN Users
                        ON Tasks.creator_id=Users.user_id;
                        """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка запроса: {e}")
    finally:
        connection.close()

def get_specific_orders(user_id):
    connection = connect_to_db()
    if not connection:
        print("Нет соединения с базой данных.")
        return None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
                        SELECT task_id, task_name, task_text FROM Tasks
                        WHERE creator_id= %s ;
                        """,
            (user_id,)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка запроса: {e}")
    finally:
        connection.close()

def get_my_tasks(exec_id):
    connection = connect_to_db()
    if not connection:
        print("Нет соединения с базой данных.")
        return None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
                        SELECT Execs.exec_id, Tasks.task_name, Tasks.task_text, Tasks.creator_id FROM Execs
                        LEFT JOIN Tasks
                        ON Execs.task_id=Tasks.task_id
                        WHERE exec_id= %s;
                        """,
            (exec_id,)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка запроса: {e}")
    finally:
        connection.close()


def get_bids_for_task(task_id):
    connection = connect_to_db()
    if not connection:
        print("Нет соединения с базой данных.")
        return None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
                        SELECT Bids.bid_id, Bids.task_id, Bids.exec_id, Bids.price, Bids.status, Users.email
                        FROM Bids 
                        LEFT JOIN Users
                        ON Bids.exec_id=Users.user_id
                        WHERE task_id= %s ;
                        """,
            (task_id,)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка запроса: {e}")
    finally:
        connection.close()

def get_user(user_id):
    connection = connect_to_db()
    if not connection:
        print("Нет соединения с базой данных.")
        return None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
                        SELECT email FROM Users
                        WHERE user_id= %s ;
                        """,
            (user_id,)
        )
        return cursor.fetchone()
    except Exception as e:
        print(f"Ошибка запроса: {e}")
    finally:
        connection.close()

def record_action(user_id, task_id, action):
    connection = connect_to_db()
    if not connection:
        print("Нет соединения с базой данных.")
        return None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
                        INSERT INTO User_actions (user_id, task_id, user_action, action_time)
                        VALUES (%s, %s, %s, NOW())
                        """,
            (user_id, task_id, action)
        )
        connection.commit()
    except Exception as e:
        print(f"Ошибка запроса: {e}")
    finally:
        connection.close()

#register_user('mail@mail.ru','god')
#add_task('coursework2','another coursework.',5)
#print(get_specific_orders(5))
#add_bid(1,5,500)
#print(add_task('order','order',7))
print(get_my_tasks(7))