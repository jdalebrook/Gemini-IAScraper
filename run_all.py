import subprocess
import webbrowser
import time

def ejecutar_todo():
    print("🌐 Iniciando Panel Web...")
    # Lanzamos la web en un proceso separado para que no bloquee
    subprocess.Popen(["python", "app.py"])

    # Esperamos 2 segundos y abrimos el navegador
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000")

    print("🛰️ Iniciando Scraper de noticias...")
    subprocess.run(["python", "scraper.py"])

    print("🧠 Iniciando Procesador de IA (Segundo plano)...")
    # Popen permite que el script siga corriendo sin esperar a que la IA termine
    subprocess.Popen(["python", "ia_processor.py"])

    print("\n✅ TODO LISTO.")
    print("La web ya está abierta. Las noticias aparecerán conforme Gemini las procese.")

if __name__ == "__main__":
    ejecutar_todo()