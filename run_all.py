import subprocess
import webbrowser
import time
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

_env = {**os.environ, "PYTHONUTF8": "1"}

def ejecutar_todo():
    python = sys.executable

    print("🗄️ 0. Inicializando base de datos...")
    subprocess.run([python, "core/database.py"], env=_env)

    print("🌐 1. Iniciando Panel Web (Flask)...")
    subprocess.Popen([python, "app.py"], env=_env)

    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000")

    print("🛰️ 2. Iniciando Scraper...")
    subprocess.run([python, "core/scraper.py"], env=_env)

    print("🧠 3. Iniciando Procesador de IA...")
    subprocess.Popen([python, "core/ia_processor.py"], env=_env)

    print("\n✅ SISTEMA EN MARCHA.")
    print("La web se actualizará automáticamente según avance el procesador de IA.")

if __name__ == "__main__":
    ejecutar_todo()
