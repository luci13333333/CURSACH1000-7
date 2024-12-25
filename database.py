import psycopg2
from config import DATABASE_URL

def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn



def create_tables(conn):
    cur = conn.cursor()

    # Создание таблицы пользователей
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(100) NOT NULL
        )
    """)

    # Создание таблицы лекций
    cur.execute("""
        CREATE TABLE IF NOT EXISTS lectures (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL
        )
    """)

    conn.commit()


# Использование функций
conn = connect_to_db()
create_tables(conn)
def insert_user(username, password_hash):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (username, password_hash) VALUES (%s, %s)
        RETURNING id
    """, (username, password_hash))
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return user_id

def get_user_by_username(username):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def insert_lecture(user_id, title):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO lectures (user_id, title) VALUES (%s, %s)
        RETURNING id
    """, (user_id, title))
    lecture_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return lecture_id

def save_lecture(lecture_id, content):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE lectures SET content = %s WHERE id = %s
    """, (content, lecture_id))
    conn.commit()
    cur.close()
    conn.close()

def get_lectures(page, per_page=ITEMS_PER_PAGE):
    conn = connect_to_db()
    cur = conn.cursor()
    offset = (page - 1) * per_page
    cur.execute("""
        SELECT l.id, u.username, l.title, l.content
        FROM lectures l
        JOIN users u ON l.user_id = u.id
        ORDER BY l.id
        LIMIT %s OFFSET %s
    """, (per_page, offset))
    lectures = cur.fetchall()
    cur.close()
    conn.close()
    return lectures

def get_lecture(lecture_id):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT l.id, l.title, l.content
        FROM lectures l
        WHERE l.id = %s
    """, (lecture_id,))
    lecture = cur.fetchone()
    cur.close()
    conn.close()
    return lecture
