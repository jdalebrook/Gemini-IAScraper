# Skully News — AI News Curator

Un sistema inteligente de curación y procesamiento de noticias técnicas con soporte para motores de IA locales y en la nube. Recolecta artículos de RSS, los traduce al español, genera resúmenes ejecutivos y los puntúa por fiabilidad.

---

## Características principales

- **Multi-fuente RSS con ponderación** — Gestión visual de feeds por categoría. Cada fuente tiene un peso (1–10) que controla cuántos artículos se extraen por ciclo.
- **Panel de gestión de feeds** — Añade, edita, elimina y repondera fuentes y categorías desde la UI sin tocar ficheros.
- **Doble motor de IA** — Soporte nativo para **Google Gemini** (free/paid) y **Ollama** (modelos locales). Seleccionable en tiempo real desde la UI.
- **Traducción y resumen automático** — Cada artículo se traduce al español con resumen ejecutivo generado por IA.
- **Anti-fake news** — Puntuación de fiabilidad 1–10 basada en calidad técnica y objetividad de la fuente.
- **Deduplicación** — SQLite con hashing MD5 para evitar procesar el mismo artículo dos veces.
- **Control de energía** — Slider de modo energético (Turbo → Eco) que regula velocidad y consumo de API.
- **Procesamiento programado** — Ventana horaria configurable (soporta franjas nocturnas, ej. 22h–06h).
- **Dark mode** — Tema claro, oscuro y sistema desde la barra de navegación.
- **Configuración en vivo** — Cambios persistidos sin reiniciar el proceso.
- **Distribuible como .exe** — Build de un clic para Windows con PyInstaller.

---

## Instalación (desarrollo)

### Requisitos
- Python 3.10+
- (Opcional) [Ollama](https://ollama.com) instalado y corriendo localmente

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/Gemini-IAScraper.git
cd Gemini-IAScraper

# 2. Crear entorno virtual e instalar dependencias
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt

# 3. Configurar claves de API
cp .env.example .env
# Editar .env:
# GEMINI_API_KEY_FREE=tu_clave_ai_studio
# GEMINI_API_KEY_PAID=tu_clave_google_cloud  (opcional)

# 4. Ejecutar
python run_all.py
```

El sistema abre automáticamente `http://127.0.0.1:5000`.

---

## Distribución Windows (.exe)

Para compartir con usuarios que no tienen Python instalado:

```bat
build_exe.bat
```

Genera `dist/Skully/` con todo incluido. El usuario solo necesita:
1. Descomprimir el `.zip`
2. Renombrar `.env.example` a `.env` y pegar su `GEMINI_API_KEY_FREE`
3. Doble clic en `Skully.exe`

> Si tiene Ollama instalado y corriendo, lo detecta automáticamente.

---

## Gestión de feeds

Los feeds se gestionan desde el panel izquierdo (**Feeds** en la navbar):

- **Añadir / editar / eliminar** fuentes RSS dentro de cada categoría
- **Crear / renombrar / eliminar** categorías completas
- **Peso de relevancia (1–10)** — controla cuántos artículos extrae el scraper por fuente en cada ciclo:

| Peso | Artículos/ciclo |
|------|----------------|
| 1    | ~2             |
| 5    | ~8 (default)   |
| 10   | ~16            |

Los ficheros `config/feeds/feeds_<categoria>.json` admiten formato simple o extendido:

```json
{
  "OpenAI":  "https://openai.com/news/rss.xml",
  "MIT_AI":  { "url": "https://technologyreview.com/.../feed", "weight": 8 }
}
```

---

## Motores de IA

### Google Gemini (nube)
Requiere `GEMINI_API_KEY_FREE` o `GEMINI_API_KEY_PAID` en `.env`.

| Modo  | Limite diario aprox. | Coste aprox./articulo |
|-------|---------------------|-----------------------|
| Free  | 100 articulos       | 0.00 EUR              |
| Paid  | 800 articulos       | 0.00012 EUR           |

### Ollama (local)
Sin API key. Instala Ollama y descarga un modelo:
```bash
ollama pull qwen2.5:14b
```
La UI lista los modelos disponibles y permite cambiar temperatura en tiempo real.

---

## Configuracion del procesador

`config/processor_config.json` — editable desde la UI sin reiniciar:

| Campo | Descripcion |
|-------|-------------|
| `engine` | `"gemini"` o `"ollama"` |
| `gemini_mode` | `"free"` o `"paid"` |
| `gemini_model` | Modelo Gemini (ej. `gemini-2.5-flash-lite`) |
| `ollama_host` | URL del servidor Ollama |
| `ollama_model` | Modelo local (ej. `qwen2.5:14b`) |
| `ollama_temperature` | Temperatura 0.0–1.0 |
| `batch_size` | Articulos por lote |
| `pause_seconds` | Pausa entre lotes |
| `energy_mode` | 0=Turbo · 25=Rapido · 50=Equilibrado · 75=Ahorro · 100=Eco |
| `schedule_enabled` | Activar ventana horaria |
| `schedule_start` / `schedule_end` | Horas de inicio y fin |
| `min_pending` | Minimo de articulos pendientes para activar el procesador |

---

## Estructura del proyecto

```
Gemini-IAScraper/
├── app.py                     # Servidor Flask + API REST
├── run_all.py                 # Orquestador (desarrollo, usa subprocesos)
├── run_bundled.py             # Orquestador para .exe (usa threads)
├── skully.spec                # Spec de PyInstaller
├── build_exe.bat              # Build de un clic para Windows
├── requirements.txt
├── .env                       # API keys (no incluido en git)
├── .env.example
│
├── app/
│   ├── templates/index.html   # Dashboard web (Bootstrap 5)
│   └── static/
│
├── core/
│   ├── database.py            # Inicializacion y migracion SQLite
│   ├── scraper.py             # Recolector RSS con soporte de pesos
│   ├── ia_processor.py        # Motor IA (Gemini / Ollama)
│   └── actions.py
│
├── config/
│   ├── processor_config.json  # Configuracion del procesador
│   └── feeds/                 # JSONs de fuentes RSS por categoria
│
└── data/                      # Generado en runtime (no en git)
    └── noticias_ia.db
```

---

Creado con Python, Flask, Bootstrap 5 y Gemini / Ollama.
