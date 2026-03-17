import feedparser
import sqlite3
import hashlib
import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "noticias_ia.db")
FEEDS_DIR = os.path.join(PROJECT_ROOT, "config", "feeds")

LIMIT_POR_CATEGORIA = 50
LIMIT_POR_FUENTE = 8

def extraer_noticias():
    archivos_feeds = [f for f in os.listdir(FEEDS_DIR) if f.startswith('feeds_') and f.endswith('.json')]

    if not archivos_feeds:
        print("⚠️ No se encontraron archivos 'feeds_*.json' en config/feeds/.")
        return

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        for archivo in archivos_feeds:
            categoria = archivo.replace('feeds_', '').replace('.json', '').upper()
            print(f"\n📂 CATEGORÍA: {categoria}")

            noticias_totales_cat = 0

            with open(os.path.join(FEEDS_DIR, archivo), "r", encoding='utf-8') as f:
                fuentes = json.load(f)

            for nombre_fuente, url_feed in fuentes.items():
                if noticias_totales_cat >= LIMIT_POR_CATEGORIA:
                    break

                print(f"  📡 {nombre_fuente.ljust(15)} |", end=" ")
                noticias_fuente = 0

                try:
                    feed = feedparser.parse(url_feed)
                    for entrada in feed.entries:
                        if noticias_fuente >= LIMIT_POR_FUENTE or noticias_totales_cat >= LIMIT_POR_CATEGORIA:
                            break

                        url = entrada.get("link", "")
                        link_hash = hashlib.md5(url.encode()).hexdigest()
                        titulo = entrada.get("title", "Sin título")

                        try:
                            cursor.execute('''
                                INSERT INTO noticias (link_hash, fuente, categoria, titulo_original, url)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (link_hash, nombre_fuente, categoria, titulo, url))

                            noticias_fuente += 1
                            noticias_totales_cat += 1

                        except sqlite3.IntegrityError:
                            continue

                    print(f"Nuevas: {noticias_fuente}")

                except Exception as e:
                    print(f"❌ Error: {e}")

            print(f"  ✅ Total {categoria}: {noticias_totales_cat} noticias.")

        conn.commit()
    print("\n✨ Scrapeo finalizado con éxito.")

if __name__ == "__main__":
    extraer_noticias()
