import subprocess
import time
import webbrowser
import os

def ejecutar():
    print("🚀 Iniciando AI News Curator 2026...")

    # 1. Ejecutar Scraper
    print("\n1. Buscando noticias nuevas...")
    subprocess.run(["python", "scraper.py"])

    # 2. Ejecutar Procesador IA (con el nuevo límite de tiempo)
    print("\n2. Analizando con Gemini (esto puede tardar por la cuota gratuita)...")
    print("Presiona Ctrl+C si quieres saltar este paso y ver lo que ya hay.")
    try:
        subprocess.run(["python", "ia_processor.py"])
    except KeyboardInterrupt:
        print("\n⏩ Procesamiento interrumpido por el usuario.")

    # 3. Lanzar la interfaz Web
    print("\n3. Abriendo panel de control...")
    # Abrimos el navegador automáticamente
    webbrowser.open("http://127.0.0.1:5000")

    # Ejecutamos la app de Flask
    subprocess.run(["python", "app.py"])

if __name__ == "__main__":
    ejecutar()