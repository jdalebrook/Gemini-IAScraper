import feedparser
import sqlite3
import hashlib
import json
import os
from datetime import datetime

DB_PATH = "noticias_ia.db"

def generar_hash(url):
    # Crea un identificador único basado en la URL
    return hashlib.md5(url.encode()).hexdigest()

def extraer_noticias():
    if not os.path.exists("feeds_rss.json"):
        print("❌ No se encuentra feeds_rss.json")
        return

    with open("feeds_rss.json", "r") as f:
        fuentes = json.load(f)

    nuevas_noticias = 0

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        for nombre_fuente, url_feed in fuentes.items():
            print(f"📡 Explorando {nombre_fuente}...")
            feed = feedparser.parse(url_feed)

            for entrada in feed.entries:
                url = entrada.get("link", "")
                link_hash = generar_hash(url)
                titulo = entrada.get("title", "")
                fecha = entrada.get("published", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                # Intentamos insertar. Si el hash ya existe, el 'UNIQUE' de SQL lo ignorará
                try:
                    cursor.execute('''
                        INSERT INTO noticias (link_hash, fuente, titulo_original, url, fecha_publicacion)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (link_hash, nombre_fuente, titulo, url, fecha))
                    nuevas_noticias += 1
                except sqlite3.IntegrityError:
                    # Esto significa que la noticia ya está en la base de datos
                    continue

        conn.commit()

    print(f"✨ Proceso terminado. Se han añadido {nuevas_noticias} noticias nuevas.")

if __name__ == "__main__":
    extraer_noticias()