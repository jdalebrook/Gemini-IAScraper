import sqlite3

def setup_db():
    conn = sqlite3.connect("noticias_ia.db")
    cursor = conn.cursor()

    # 1. Crear la tabla si no existe (con todas las columnas)
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

    # 2. SEGURO ANTI-ERRORES: Intentar añadir las columnas una a una
    # por si la tabla ya existía de antes sin ellas.
    columnas_nuevas = ["categoria", "etiquetas"]
    for col in columnas_nuevas:
        try:
            cursor.execute(f'ALTER TABLE noticias ADD COLUMN {col} TEXT')
            print(f"✅ Columna '{col}' añadida con éxito.")
        except sqlite3.OperationalError:
            # Si entra aquí es porque la columna ya existe, así que no hacemos nada
            print(f"ℹ️ La columna '{col}' ya estaba presente.")

    conn.commit()
    conn.close()
    print("🚀 Base de datos sincronizada y lista.")

if __name__ == "__main__":
    setup_db()