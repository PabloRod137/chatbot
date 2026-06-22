import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "chatbot.db")

def init_db():
    db_path_dynamic = os.getenv("DB_PATH", "chatbot.db")
    conn = sqlite3.connect(db_path_dynamic)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_message(phone_number: str, role: str, content: str):
    db_path_dynamic = os.getenv("DB_PATH", "chatbot.db")
    conn = sqlite3.connect(db_path_dynamic)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (phone_number, role, content)
        VALUES (?, ?, ?)
    ''', (phone_number, role, content))
    conn.commit()
    conn.close()

def get_history(phone_number: str, limit: int = 10) -> list:
    # Límite estricto de historial para proteger el consumo de tokens y asegurar un contexto relevante
    max_limit = min(limit, 10)
    
    # Nos aseguramos de obtener la ruta dinámicamente si cambia
    db_path_dynamic = os.getenv("DB_PATH", "chatbot.db")
    conn = sqlite3.connect(db_path_dynamic)
    cursor = conn.cursor()
    
    # Obtenemos los últimos 'max_limit' mensajes
    cursor.execute('''
        SELECT role, content FROM messages
        WHERE phone_number = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (phone_number, max_limit))
    rows = cursor.fetchall()
    conn.close()
    
    # Invertimos la lista para que queden en orden cronológico (el más antiguo primero)
    rows.reverse()
    
    return [{"role": row[0], "content": row[1]} for row in rows]
