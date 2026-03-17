import sqlite3

with sqlite3.connect("noticias_ia.db") as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT titular_es, score_fiabilidad FROM noticias WHERE titular_es IS NOT NULL')
    for fila in cursor.fetchall():
        print(f"🔹 {fila[0]} | Fiabilidad: {fila[1]}/10")