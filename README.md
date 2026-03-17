# 🤖 AI News Curator 2026
Un sistema inteligente de curación de noticias sobre Inteligencia Artificial para blogs y redes sociales. Utiliza Gemini Flash (Latest) para filtrar ruido, traducir y puntuar la veracidad de la información de forma eficiente.

# ✨ Características principales
* ** 🌐 Multi-fuente RSS: Recolecta noticias de OpenAI, MIT, VentureBeat y más.

* ** 🧠 Inteligencia Gemini: Traducción automática al español y resúmenes ejecutivos usando la SDK de última generación (google-genai).

* ** 🛡️ Filtro de Anti-Fake News: Sistema de puntuación (1-10) basado en calidad técnica y objetividad.

* ** 🗄️ Control de Duplicados: Base de datos SQLite con hashing para evitar procesar la misma noticia dos veces.

* ** 💻 Panel de Control Web: Interfaz Flask para gestionar favoritos u ocultar noticias.

# 🚀 Instalación rápida
Clonar el repositorio:
git clone https://github.com/tu-usuario/Gemini-IAScraper.git
cd Gemini-IAScraper

# Crear entorno virtual e instalar dependencias:
```bash
python -m venv venv
venv\Scripts\activate
pip install google-genai feedparser python-dotenv flask
```
# Configurar variables de entorno:
Crea un archivo .env en la raíz con:
GEMINI_API_KEY=tu_clave_de_google_ai_studio

# Ejecutar el sistema:
```bash
python run_all.py
```
# 🛠️ Estructura de Archivos
scraper.py: Recolector de feeds RSS optimizado (50 noticias por categoría).

ia_processor.py: El cerebro que utiliza gemini-flash-latest con modo ahorro/pago.

app.py: Servidor Flask para la interfaz visual.

database.py: Gestión y estructura de la base de datos SQL.

# Creado con ❤️ y Gemini Flash.

# 🚀 Último paso: El archivo run_all.py
Para que la instrucción python run_all.py del README funcione perfecta, asegúrate de que tu archivo run_all.py tenga este orden lógico:

Python
import subprocess
import time

def ejecutar_sistema():
print("📡 1. Iniciando recolección de noticias (Scraper)...")
subprocess.run(["python", "scraper.py"])

    print("\n🤖 2. Procesando noticias con IA (Gemini)...")
    # Esto lanza el procesador. Se detendrá según tu configuración de MODO_PAGO
    subprocess.run(["python", "ia_processor.py"])

if __name__ == "__main__":
ejecutar_sistema()


