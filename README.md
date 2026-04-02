# Skully News — AI News Curator

Un sistema inteligente de curación y procesamiento de noticias técnicas con soporte para motores de IA locales y en la nube. Recolecta artículos de RSS, los traduce al español, genera resúmenes ejecutivos y los puntúa por fiabilidad.

---

## Características principales

- **Multi-fuente RSS** — 17 categorías de feeds: IA, ML Engineering, MLOps, GCP, Cloud Architecture, Kubernetes, Seguridad, Ciberseguridad, Vulnerabilidades, Frontend, Python, Avances Tecnológicos, Avances Informáticos, Tecnología, Cosmos, Física y Psicología.
- **Doble motor de IA** — Soporte nativo para **Google Gemini** (free/paid tier) y **Ollama** (modelos locales como `qwen2.5:14b`). Seleccionable en tiempo real desde la UI.
- **Traducción y resumen automático** — Cada artículo se traduce al español y recibe un resumen ejecutivo generado por IA.
- **Anti-fake news** — Puntuación de fiabilidad 1–10 basada en calidad técnica y objetividad de la fuente.
- **Deduplicación** — SQLite con hashing MD5 para evitar procesar el mismo artículo dos veces.
- **Control de energía** — Slider de modo energético (0–100) que regula la velocidad de procesamiento para ajustar el consumo de CPU y cuota de API.
- **Procesamiento programado** — Ventana horaria configurable para ejecutar el procesador solo en horas definidas (ej. 02:00–07:00).
- **Dark mode** — Alternancia entre tema claro, oscuro y sistema desde la barra de navegación.
- **Panel de control web** — Dashboard Bootstrap 5 con filtros por categoría, marcado de favoritos/importantes, archivado y ocultado de noticias.
- **Configuración en vivo** — Offcanvas de configuración que persiste cambios sin reiniciar el proceso.
- **Estado del procesador** — Indicador visual (running/paused/stopped) y control de pausa/reanudación desde la UI.

---

## Estructura del proyecto

```
Gemini-IAScraper/
├── app.py                    # Servidor Flask (entry point web)
├── run_all.py                # Orquestador principal
├── requirements.txt
├── .env                      # API keys (no incluido en git)
├── .env.example
│
├── app/
│   ├── templates/
│   │   └── index.html        # Dashboard web (Bootstrap 5)
│   └── static/
│       ├── icon.ico
│       └── icon128.png
│
├── core/
│   ├── database.py           # Inicialización y migración de SQLite
│   ├── scraper.py            # Recolector de feeds RSS
│   ├── ia_processor.py       # Motor de IA (Gemini / Ollama)
│   └── actions.py            # Lógica de negocio
│
├── config/
│   ├── processor_config.json # Configuración del procesador
│   └── feeds/                # 17 archivos JSON con URLs de RSS por categoría
│
├── scripts/
│   ├── check_results.py      # Verifica resultados del procesamiento
│   ├── debug_models.py       # Debug de modelos disponibles
│   ├── lista_modelos.py      # Lista modelos Ollama detectados
│   └── IAScrapper.bat        # Lanzador Windows
│
└── data/
    ├── noticias_ia.db        # Base de datos SQLite
    └── processor.state       # Estado del procesador (IPC entre procesos)
```

---

## Instalación

### Requisitos
- Python 3.10+
- (Opcional) [Ollama](https://ollama.com) instalado y corriendo localmente

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/Gemini-IAScraper.git
cd Gemini-IAScraper

# 2. Crear entorno virtual e instalar dependencias
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env y añadir tus claves:
# GEMINI_API_KEY_FREE=tu_clave_ai_studio
# GEMINI_API_KEY_PAID=tu_clave_google_cloud

# 4. Ejecutar
python run_all.py
```

El sistema abrirá automáticamente `http://127.0.0.1:5000` en el navegador.

---

## Configuración del procesador

El archivo `config/processor_config.json` controla el comportamiento del motor:

| Campo | Descripción |
|---|---|
| `engine` | `"gemini"` o `"ollama"` |
| `gemini_mode` | `"free"` (límite ~100/día) o `"paid"` (~800/día) |
| `gemini_model` | Modelo Gemini a usar (ej. `gemini-2.5-flash-lite`) |
| `ollama_host` | URL del servidor Ollama |
| `ollama_model` | Modelo local (ej. `qwen2.5:14b`) |
| `ollama_temperature` | Temperatura de generación (0.0–1.0) |
| `batch_size` | Artículos procesados por lote |
| `pause_seconds` | Pausa entre lotes |
| `energy_mode` | Velocidad de procesamiento (0=mínimo, 100=máximo) |
| `schedule_enabled` | Activar ventana horaria programada |
| `schedule_start` / `schedule_end` | Horas de inicio y fin del procesamiento |

Todos los campos son editables desde el panel web sin necesidad de reiniciar.

---

## Motores de IA soportados

### Google Gemini (nube)
Requiere `GEMINI_API_KEY_FREE` o `GEMINI_API_KEY_PAID` en `.env`. Compatible con cualquier modelo `gemini-*` disponible en AI Studio / Google Cloud.

### Ollama (local)
No requiere API key. Instala Ollama y descarga un modelo:
```bash
ollama pull qwen2.5:14b
```
El sistema detecta automáticamente los modelos disponibles y los lista en la UI.

---

Creado con Python, Flask y Gemini / Ollama.