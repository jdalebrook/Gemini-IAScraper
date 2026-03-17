import subprocess
import webbrowser
import time

def ejecutar_todo():
    print("🌐 1. Iniciando Panel Web (Flask)...")
    subprocess.Popen(["python", "app.py"])

    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000")

    print("🛰️ 2. Iniciando Scraper...")
    subprocess.run(["python", "core/scraper.py"])

    print("🧠 3. Iniciando Procesador de IA...")
    subprocess.Popen(["python", "core/ia_processor.py"])

    print("\n✅ SISTEMA EN MARCHA.")
    print("La web se actualizará automáticamente según avance Gemini.")

if __name__ == "__main__":
    ejecutar_todo()
