import os
import sqlite3

def create_tables():
    if not os.path.exists("./database/database.db"):
        conn = sqlite3.connect("./database/database.db")
        cursor = conn.cursor()
        # Создаём таблицу, если её ещё нет
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT PRIMARY KEY, username VARCHAR(50) UNIQUE NOT NULL, password_hash INT(100) NOT NULL)")
        conn.commit()
        conn.close()
        conn = sqlite3.connect("./database/database.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS lectures (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id), title VARCHAR(255) NOT NULL, content TEXT NOT NULL)")
        conn.commit()
        conn.close()
