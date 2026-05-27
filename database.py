import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

def create_users_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        password VARCHAR(255),
        role VARCHAR(20)
    )
    """)
    cursor.execute(""" CREATE TABLE IF NOT EXISTS logs (
       id INT AUTO_INCREMENT PRIMARY KEY,
       employee_id INT,
       risk_score FLOAT,
       decision VARCHAR(50),
       explanation TEXT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP) """)

    conn.commit()
    conn.close()

def init_db():
    # existing code...
    create_users_table()

    # create default admin (only once)
    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("""
       
INSERT INTO users (username, password, role)
VALUES ('admin', '$2b$12$tvlyJWIYSHvTNaLV8sqm1u1eOecJkG7XubjDOHnU27qMe3X.k.OhS', 'admin');
        """)
    conn.commit()
    conn.close()