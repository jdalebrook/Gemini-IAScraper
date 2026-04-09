import sqlite3
import os
import sys

PROJECT_ROOT = (os.path.dirname(sys.executable) if getattr(sys, 'frozen', False)
                else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "noticias_ia.db")

def setup_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS noticias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link_hash TEXT UNIQUE,
            fuente TEXT,
            categoria TEXT,
            titulo_original TEXT,
            url TEXT,
            fecha_publicacion TEXT,
            titular_es TEXT,
            resumen_es TEXT,
            score_fiabilidad INTEGER,
            analisis_objetivo TEXT,
            estado TEXT DEFAULT 'nuevo',
            etiquetas TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    columnas_nuevas = ["categoria", "etiquetas"]
    for col in columnas_nuevas:
        try:
            cursor.execute(f'ALTER TABLE noticias ADD COLUMN {col} TEXT')
            print(f"✅ Columna '{col}' añadida con éxito.")
        except sqlite3.OperationalError:
            print(f"ℹ️ La columna '{col}' ya estaba presente.")

    conn.commit()
    conn.close()
    print("🚀 Base de datos sincronizada y lista.")

if __name__ == "__main__":
    setup_db()
