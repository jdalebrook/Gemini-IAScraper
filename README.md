# 🤖 AI News Curator 2026

Un sistema inteligente de curación de noticias sobre Inteligencia Artificial, diseñado para potenciar la creación de contenido en blogs y redes sociales. Este proyecto utiliza **Gemini 2.5 Flash** para filtrar el ruido, traducir titulares y puntuar la veracidad de la información de forma totalmente gratuita.

## ✨ Características principales

* **🌐 Multi-fuente RSS:** Recolecta noticias de OpenAI, MIT, VentureBeat y más.
* **🧠 Inteligencia Gemini:** Traducción automática al español y resúmenes ejecutivos.
* **🛡️ Filtro de Anti-Fake News:** Sistema de puntuación (1-10) basado en la objetividad y calidad técnica del contenido.
* **🗄️ Control de Duplicados:** Base de datos SQLite que evita procesar la misma noticia dos veces.
* **💻 Panel de Control Web:** Interfaz limpia para gestionar favoritos, ocultar noticias o marcar temas para el blog.

README.md (Versión a prueba de errores)
Copia desde la línea de abajo hasta el final:

#🤖 AI News Curator 2026
Un sistema inteligente de curación de noticias sobre Inteligencia Artificial para blogs y redes sociales. Utiliza Gemini 2.5 Flash para filtrar ruido, traducir y puntuar la veracidad de la información gratis.

## ✨ Características principales
* **Multi-fuente RSS:** Recolecta noticias de OpenAI, MIT, VentureBeat y más.

* **Inteligencia Gemini: **Traducción automática al español y resúmenes ejecutivos.

* **Filtro de Anti-Fake News: **Sistema de puntuación (1-10) basado en calidad técnica.

* **Control de Duplicados:** Base de datos SQLite que evita repetir noticias.

* **Panel de Control Web:** Interfaz para gestionar favoritos u ocultar noticias.

## 🚀 Instalación rápida
Clonar el repositorio:
Usa el comando git clone con la URL de tu repositorio y entra en la carpeta.

Crear entorno virtual e instalar dependencias:
```bash
python -m venv venv

venv\Scripts\activate (en Windows)

pip install google-generativeai feedparser python-dotenv flask
```
## Configurar variables de entorno:
* Crea un archivo .env en la raíz con:
```bash
GEMINI_API_KEY=tu_clave_de_google_ai_studio

DB_NAME=noticias_ia.db
```
## Ejecutar el sistema:
```bash
python database.py (crea la DB)

python run_all.py (inicia todo)
```
## 🛠️ Estructura de Archivos
scraper.py: Recolector de feeds RSS.
```bash
ia_processor.py: El cerebro con Gemini 2.5 Flash.

app.py: Servidor Flask para la interfaz.

database.py: Gestión de SQL.
```
### Creado con ❤️ y Gemini 2.5 Flash.