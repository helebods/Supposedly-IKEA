from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector


def db_connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="users"
    )


def register_user(username, password):
    conn = db_connect()
    cursor = conn.cursor()

    hashed_password = generate_password_hash(password)

    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                   (username, hashed_password))
    conn.commit()
    cursor.close()
    conn.close()

    return True


def login_user(username, password):
    conn = db_connect()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT user_id, username, password FROM users WHERE username = %s",
        (username,)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return user
    else:
        print(user, password)

    return None
