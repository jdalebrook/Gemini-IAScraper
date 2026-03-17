import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_NAME", "noticias_ia.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS noticias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link_hash TEXT UNIQUE,          -- Para evitar duplicados
                fuente TEXT,
                titulo_original TEXT,
                url TEXT,
                fecha_publicacion TEXT,
                titular_es TEXT,                -- IA
                resumen_es TEXT,                -- IA
                score_fiabilidad INTEGER,       -- IA (1-10)
                analisis_objetivo TEXT,         -- IA
                estado TEXT DEFAULT 'nuevo',    -- nuevo, favorito, oculto
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    print(f"✅ Base de datos lista en: {DB_PATH}")

if __name__ == "__main__":
    init_db()