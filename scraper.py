import feedparser
import sqlite3
import hashlib
import json
import os

DB_PATH = "noticias_ia.db"

def extraer_noticias():
    # 1. Buscar todos los archivos de feeds en la carpeta actual
    archivos_feeds = [f for f in os.listdir('.') if f.startswith('feeds_') and f.endswith('.json')]

    if not archivos_feeds:
        print("⚠️ No se encontraron archivos 'feeds_*.json'. Revisa los nombres.")
        return

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        for archivo in archivos_feeds:
            # Extraemos el nombre de la categoría del nombre del archivo
            # Ejemplo: 'feeds_cosmos.json' -> 'COSMOS'
            categoria = archivo.replace('feeds_', '').replace('.json', '').upper()

            print(f"\n📂 Procesando categoría: {categoria}")

            with open(archivo, "r", encoding='utf-8') as f:
                fuentes = json.load(f)

            for nombre_fuente, url_feed in fuentes.items():
                print(f"  📡 Explorando {nombre_fuente}...")
                try:
                    feed = feedparser.parse(url_feed)
                    for entrada in feed.entries:
                        url = entrada.get("link", "")
                        # Creamos un hash único para no duplicar noticias
                        link_hash = hashlib.md5(url.encode()).hexdigest()

                        titulo = entrada.get("title", "Sin título")

                        try:
                            cursor.execute('''
                                INSERT INTO noticias (link_hash, fuente, categoria, titulo_original, url)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (link_hash, nombre_fuente, categoria, titulo, url))
                        except sqlite3.IntegrityError:
                            # Si ya existe, simplemente pasamos a la siguiente
                            continue
                except Exception as e:
                    print(f"  ❌ Error en fuente {nombre_fuente}: {e}")

        conn.commit()
    print("\n✅ ¡Scrapeo multitemático completado!")

if __name__ == "__main__":
    extraer_noticias()