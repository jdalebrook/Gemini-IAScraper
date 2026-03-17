import subprocess
import webbrowser
import time
import os

def ejecutar_todo():
    # Detectamos si los archivos están en la raíz o en /core
    scraper_path = "core/scraper.py" if os.path.exists("core/scraper.py") else "scraper.py"
    processor_path = "core/ia_processor.py" if os.path.exists("core/ia_processor.py") else "ia_processor.py"

    print("🌐 1. Iniciando Panel Web (Flask)...")
    # app.py se queda en la raíz normalmente para Flask
    subprocess.Popen(["python", "app.py"])

    # Esperamos a que el servidor arranque antes de abrir el navegador
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000")

    print(f"🛰️ 2. Iniciando Scraper desde {scraper_path}...")
    # Usamos run para que termine de recoger noticias antes de pasar a la IA
    subprocess.run(["python", scraper_path])

    print(f"🧠 3. Iniciando Procesador de IA desde {processor_path}...")
    # Popen para que la IA trabaje mientras tú navegas por la web
    subprocess.Popen(["python", processor_path])

    print("\n✅ SISTEMA EN MARCHA.")
    print("La web se actualizará automáticamente según avance Gemini.")

if __name__ == "__main__":
    ejecutar_todo()