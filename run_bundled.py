"""
Entry point para el build de PyInstaller.
Usa threads en lugar de subprocesos (run_all.py sigue funcionando para desarrollo).
"""
import sys
import os
import threading
import webbrowser
import time

sys.stdout.reconfigure(encoding='utf-8')

# Aseguramos que data/ y config/ existen junto al exe antes de importar nada
_ROOT = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(_ROOT, "data"),          exist_ok=True)
os.makedirs(os.path.join(_ROOT, "config", "feeds"), exist_ok=True)


def _run_flask():
    from app import app
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False, threaded=True)


def _run_scraper(interval_hours, ready_event):
    from core.scraper import run_loop_scraper
    run_loop_scraper(interval_hours, ready_event)


def _run_processor():
    from core import ia_processor
    ia_processor.run_loop()


def _get_scrape_interval():
    import json
    config_path = os.path.join(_ROOT, "config", "processor_config.json")
    try:
        with open(config_path) as f:
            return max(1, int(json.load(f).get("scrape_interval_hours", 8)))
    except Exception:
        return 8


def main():
    print("🗄️  Inicializando base de datos...")
    from core.database import setup_db
    setup_db()

    print("🌐 Iniciando Panel Web (Flask)...")
    threading.Thread(target=_run_flask, daemon=True, name="Flask").start()

    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000")

    interval = _get_scrape_interval()
    scraper_ready = threading.Event()
    print(f"🛰️  Iniciando Scraper periódico (cada {interval}h)...")
    threading.Thread(target=_run_scraper, args=(interval, scraper_ready),
                     daemon=True, name="Scraper").start()

    print("⏳ Esperando primer scraping antes de arrancar el procesador...")
    scraper_ready.wait()

    print("🧠 Iniciando Procesador IA...")
    threading.Thread(target=_run_processor, daemon=True, name="Procesador").start()

    print("\n✅ SISTEMA EN MARCHA — cierra esta ventana para detener.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Cerrando Skully News...")


if __name__ == '__main__':
    main()
