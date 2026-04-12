import feedparser
import sqlite3
import hashlib
import json
import os
import sys
import time
from datetime import datetime

PROJECT_ROOT = (os.path.dirname(sys.executable) if getattr(sys, 'frozen', False)
                else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH        = os.path.join(PROJECT_ROOT, "data", "noticias_ia.db")
FEEDS_DIR      = os.path.join(PROJECT_ROOT, "config", "feeds")
SCRAPER_STATE  = os.path.join(PROJECT_ROOT, "data", "scraper.state")

LIMIT_POR_CATEGORIA = 50
LIMIT_POR_FUENTE    = 8   # peso 5 (default)
CHUNK_INTERCALADO   = 5   # artículos por categoría por vuelta al insertar

def _source_url(val):
    return val if isinstance(val, str) else val.get("url", "")

def _source_limit(val):
    """Escala el límite de artículos según el peso (1-10). Peso 5 = límite base."""
    if isinstance(val, str):
        return LIMIT_POR_FUENTE
    weight = max(1, min(10, int(val.get("weight", 5))))
    return max(2, int(LIMIT_POR_FUENTE * weight / 5))

def _fetch_categoria(archivo):
    """Parsea todos los feeds de una categoría y devuelve lista de entradas."""
    categoria = archivo.replace('feeds_', '').replace('.json', '').upper()
    print(f"\n📂 {categoria}")

    with open(os.path.join(FEEDS_DIR, archivo), "r", encoding='utf-8') as f:
        fuentes = json.load(f)

    entradas = []
    for nombre_fuente, val_fuente in fuentes.items():
        url_feed     = _source_url(val_fuente)
        limit_fuente = _source_limit(val_fuente)
        try:
            feed  = feedparser.parse(url_feed)
            count = 0
            for entrada in feed.entries:
                if count >= limit_fuente:
                    break
                url = entrada.get("link", "")
                if not url:
                    continue
                titulo  = entrada.get("title", "Sin título")
                summary = entrada.get("summary", "") or entrada.get("description", "")
                titulo_completo = f"{titulo}\n\n{summary}".strip() if summary else titulo
                entradas.append((
                    hashlib.md5(url.encode()).hexdigest(),
                    nombre_fuente,
                    titulo_completo,
                    url,
                ))
                count += 1
            print(f"  📡 {nombre_fuente.ljust(20)} → {count} entradas")
        except Exception as e:
            print(f"  ❌ {nombre_fuente}: {e}")

    # Respetar límite por categoría
    return categoria, entradas[:LIMIT_POR_CATEGORIA]

def extraer_noticias():
    archivos_feeds = sorted([
        f for f in os.listdir(FEEDS_DIR)
        if f.startswith('feeds_') and f.endswith('.json')
    ])

    if not archivos_feeds:
        print("⚠️ No se encontraron archivos 'feeds_*.json' en config/feeds/.")
        return

    # ── Fase 1: obtener entradas de todos los feeds ────────────────────────────
    print("🛰️  Obteniendo feeds...")
    cola = {}  # {categoria: [entradas]}
    for archivo in archivos_feeds:
        categoria, entradas = _fetch_categoria(archivo)
        cola[categoria] = entradas

    # ── Fase 2: insertar en round-robin (CHUNK_INTERCALADO por categoría) ──────
    print(f"\n📥 Insertando en BD (intercalado, {CHUNK_INTERCALADO} por categoría por vuelta)...")
    nuevas_total = 0
    posicion = {cat: 0 for cat in cola}

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        while True:
            hubo_avance = False
            for categoria, entradas in cola.items():
                pos   = posicion[categoria]
                chunk = entradas[pos : pos + CHUNK_INTERCALADO]
                if not chunk:
                    continue
                nuevas_cat = 0
                for link_hash, fuente, titulo_completo, url in chunk:
                    try:
                        cursor.execute(
                            "INSERT INTO noticias (link_hash, fuente, categoria, titulo_original, url) "
                            "VALUES (?, ?, ?, ?, ?)",
                            (link_hash, fuente, categoria, titulo_completo, url),
                        )
                        nuevas_cat += 1
                        nuevas_total += 1
                    except sqlite3.IntegrityError:
                        pass
                posicion[categoria] = pos + CHUNK_INTERCALADO
                if nuevas_cat:
                    hubo_avance = True

            if not hubo_avance:
                break

        conn.commit()

    totales = {cat: len(e) for cat, e in cola.items()}
    for cat, n in totales.items():
        print(f"  {cat.ljust(30)} {n} entradas")
    print(f"\n✨ Scrapeo finalizado — {nuevas_total} noticias nuevas insertadas.")

def _write_scraper_state(interval_hours):
    with open(SCRAPER_STATE, "w") as f:
        json.dump({
            "last_scrape": datetime.now().isoformat(timespec="seconds"),
            "interval_hours": interval_hours,
        }, f)


def run_loop_scraper(interval_hours=8, ready_event=None):
    """Ejecuta scraping al arrancar y luego cada interval_hours horas.

    ready_event: threading.Event opcional; se activa tras el primer scraping
    para que el procesador IA pueda arrancar en cuanto haya datos.
    """
    while True:
        print(f"\n🛰️  [SCRAPER] Iniciando ronda ({datetime.now().strftime('%H:%M')})")
        extraer_noticias()
        _write_scraper_state(interval_hours)
        if ready_event is not None:
            ready_event.set()
            ready_event = None  # solo señalizar la primera vez
        next_dt = datetime.fromtimestamp(time.time() + interval_hours * 3600)
        print(f"🕐 [SCRAPER] Próxima ronda a las {next_dt.strftime('%H:%M')} "
              f"(en {interval_hours}h)")
        time.sleep(interval_hours * 3600)


if __name__ == "__main__":
    extraer_noticias()
