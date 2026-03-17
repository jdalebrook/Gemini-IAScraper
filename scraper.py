import feedparser
import sqlite3
import hashlib
import json
import os

DB_PATH = "noticias_ia.db"
# 1. Definimos el límite aquí para que sea fácil de cambiar en el futuro
LIMIT_POR_CATEGORIA = 50

def extraer_noticias():
    # Buscar todos los archivos de feeds en la carpeta actual
    archivos_feeds = [f for f in os.listdir('.') if f.startswith('feeds_') and f.endswith('.json')]

    if not archivos_feeds:
        print("⚠️ No se encontraron archivos 'feeds_*.json'. Revisa los nombres.")
        return

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        for archivo in archivos_feeds:
            categoria = archivo.replace('feeds_', '').replace('.json', '').upper()
            print(f"\n📂 Procesando categoría: {categoria}")

            # 2. Inicializamos el contador para esta categoría específica
            noticias_guardadas = 0

            with open(archivo, "r", encoding='utf-8') as f:
                fuentes = json.load(f)

            for nombre_fuente, url_feed in fuentes.items():
                # 3. Si ya alcanzamos el límite, no abrimos más fuentes de esta categoría
                if noticias_guardadas >= LIMIT_POR_CATEGORIA:
                    break

                print(f"  📡 Explorando {nombre_fuente}...")
                try:
                    feed = feedparser.parse(url_feed)
                    for entrada in feed.entries:
                        # 4. Verificación de seguridad dentro del bucle de noticias
                        if noticias_guardadas >= LIMIT_POR_CATEGORIA:
                            break

                        url = entrada.get("link", "")
                        link_hash = hashlib.md5(url.encode()).hexdigest()
                        titulo = entrada.get("title", "Sin título")

                        try:
                            cursor.execute('''
                                INSERT INTO noticias (link_hash, fuente, categoria, titulo_original, url)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (link_hash, nombre_fuente, categoria, titulo, url))

                            # 5. Solo sumamos al contador si la noticia es NUEVA
                            noticias_guardadas += 1

                        except sqlite3.IntegrityError:
                            # Si ya existe en la DB, no cuenta para el límite de "nuevas"
                            continue
                except Exception as e:
                    print(f"  ❌ Error en fuente {nombre_fuente}: {e}")

            print(f"  ✅ Total nuevas en {categoria}: {noticias_guardadas}")

        conn.commit()
    print("\n✅ ¡Scrapeo optimizado (50 por categoría) completado!")

if __name__ == "__main__":
    extraer_noticias()