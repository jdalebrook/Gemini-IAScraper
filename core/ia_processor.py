import os
import sqlite3
import json
import time
from datetime import datetime
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
DB_PATH     = os.path.join(PROJECT_ROOT, "data", "noticias_ia.db")
ESTADO_PATH = os.path.join(PROJECT_ROOT, "data", "processor.state")
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "processor_config.json")

LIMITE_DIARIO_FREE  = 100
LIMITE_DIARIO_PAID  = 800
PRECIO_APROX_NOTICIA = 0.00012

# ── Helpers de estado ──────────────────────────────────────────────────────────

def get_estado():
    try:
        with open(ESTADO_PATH) as f:
            return f.read().strip()
    except FileNotFoundError:
        return "running"

def set_estado(estado):
    with open(ESTADO_PATH, "w") as f:
        f.write(estado)

def get_config():
    """Lee la config en cada ciclo para reflejar cambios desde la web."""
    defaults = {
        "engine": "gemini",
        "gemini_mode": "free",
        "gemini_model": "gemini-2.5-flash-lite",
        "ollama_host": "http://localhost:11434",
        "ollama_model": "qwen2.5:14b",
        "ollama_temperature": 0.1,
        "batch_size": 5,
        "pause_seconds": 5,
    }
    try:
        with open(CONFIG_PATH) as f:
            data = json.load(f)
            return {**defaults, **data}
    except Exception:
        return defaults

# ── Llamadas a LLM ────────────────────────────────────────────────────────────

PROMPT_TEMPLATE = (
    "Analiza esta noticia: \"{titulo}\". "
    "Responde ÚNICAMENTE con un objeto JSON válido con estas claves: "
    "titular_es (traducción profesional al español), "
    "resumen_es (resumen en una frase), "
    "score (entero del 1 al 10, siendo 10 ciencia probada y 1 rumor/clickbait), "
    "razon (breve explicación del score). "
    "No añadas texto fuera del JSON."
)

def llamar_gemini(titulo, config):
    from google import genai
    from google.genai import types

    modo_pago = config["gemini_mode"] == "paid"
    api_key = os.getenv("GEMINI_API_KEY_PAID") if modo_pago else os.getenv("GEMINI_API_KEY_FREE")
    if not api_key:
        raise ValueError("Falta GEMINI_API_KEY en el .env")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=config["gemini_model"],
        contents=PROMPT_TEMPLATE.format(titulo=titulo),
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return json.loads(response.text)

def llamar_ollama(titulo, config):
    import ollama

    response = ollama.chat(
        model=config["ollama_model"],
        messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(titulo=titulo)}],
        format="json",
        options={"temperature": config["ollama_temperature"]},
    )
    return json.loads(response.message.content)

def llamar_llm(titulo, config):
    if config["engine"] == "ollama":
        return llamar_ollama(titulo, config)
    return llamar_gemini(titulo, config)

# ── Stats ──────────────────────────────────────────────────────────────────────

def obtener_stats_hoy(config):
    hoy = datetime.now().strftime("%Y-%m-%d")
    modo_pago = config.get("gemini_mode") == "paid" and config.get("engine") == "gemini"
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM noticias WHERE titular_es IS NOT NULL AND created_at >= ?",
                (hoy,)
            )
            total = cursor.fetchone()[0]
            limite = LIMITE_DIARIO_PAID if modo_pago else LIMITE_DIARIO_FREE
            coste  = round(total * PRECIO_APROX_NOTICIA, 4) if modo_pago else 0.0
            return total, coste, limite
    except Exception:
        return 0, 0.0, LIMITE_DIARIO_FREE

# ── Bucle principal ────────────────────────────────────────────────────────────

def check_schedule(config):
    """Devuelve True si estamos dentro del horario permitido."""
    if not config.get("schedule_enabled", False):
        return True
    hora   = datetime.now().hour
    start  = config.get("schedule_start", 2)
    end    = config.get("schedule_end", 7)
    if start <= end:
        return start <= hora < end
    # Franja nocturna que cruza medianoche (ej. 22h → 06h)
    return hora >= start or hora < end

def procesar_lote():
    config = get_config()
    engine = config["engine"]
    batch  = config["batch_size"]
    pausa  = config["pause_seconds"]

    # ── Comprobación de horario ────────────────────────────────────────────────
    if not check_schedule(config):
        start = config.get("schedule_start", 2)
        end   = config.get("schedule_end", 7)
        print(f"🕐 Fuera de horario permitido ({start:02d}h–{end:02d}h). Durmiendo 30 min...")
        return "SCHEDULE"

    # ── Umbral mínimo de noticias pendientes ───────────────────────────────────
    min_pending = config.get("min_pending", 0)
    if min_pending > 0:
        with sqlite3.connect(DB_PATH) as _conn:
            pendientes = _conn.execute(
                "SELECT COUNT(*) FROM noticias WHERE titular_es IS NULL"
            ).fetchone()[0]
        if pendientes < min_pending:
            print(f"📦 Pendientes ({pendientes}) < umbral ({min_pending}). Esperando acumulación...")
            return False

    procesadas_hoy, gasto_hoy, limite_hoy = obtener_stats_hoy(config)

    # Límites diarios solo aplican a Gemini
    if engine == "gemini":
        if procesadas_hoy >= limite_hoy:
            modo = config["gemini_mode"]
            estado = "paused_cost" if modo == "paid" else "paused_limit"
            print(f"🛑 Límite diario alcanzado ({procesadas_hoy}/{limite_hoy}) — auto-pausando")
            set_estado(estado)
            return "STOP"

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM noticias WHERE titular_es IS NULL ORDER BY id DESC LIMIT {batch}"
        )
        filas = cursor.fetchall()

        if not filas:
            return False

        tag = f"🤖 OLLAMA [{config['ollama_model']}]" if engine == "ollama" else f"✨ GEMINI [{config['gemini_model']}]"
        print(f"{tag} | Procesadas hoy: {procesadas_hoy}/{limite_hoy} | Coste: {gasto_hoy}€ | Lote: {len(filas)}")

        for fila in filas:
            try:
                data = llamar_llm(fila["titulo_original"], config)

                cursor.execute(
                    """UPDATE noticias SET
                       titular_es=?, resumen_es=?, score_fiabilidad=?, analisis_objetivo=?
                       WHERE id=?""",
                    (
                        data.get("titular_es", "Sin título"),
                        data.get("resumen_es", "Sin resumen"),
                        data.get("score", 5),
                        data.get("razon", ""),
                        fila["id"],
                    ),
                )
                conn.commit()
                print(f"  ✅ [{data.get('score')}/10] {data.get('titular_es', '')[:55]}...")
                time.sleep(pausa)

            except Exception as e:
                if "429" in str(e):
                    print("🛑 Cuota agotada temporalmente. Esperando 60s...")
                    time.sleep(60)
                else:
                    print(f"⚠️  Error en noticia {fila['id']}: {e}")
                break

    return True


if __name__ == "__main__":
    print("--- INICIANDO PROCESADOR ---")
    set_estado("running")
    while True:
        try:
            estado = get_estado()
            if estado in ("paused", "paused_cost", "paused_limit"):
                print(f"⏸️  Pausado [{estado}]. Comprobando en 60s...")
                time.sleep(60)
                continue

            res = procesar_lote()
            if res == "STOP":
                time.sleep(3600)
            elif res == "SCHEDULE":
                time.sleep(1800)
            elif not res:
                print("☕ Todo procesado. Esperando 10 min...")
                time.sleep(600)

        except KeyboardInterrupt:
            print("\n👋 Cerrando procesador...")
            set_estado("stopped")
            break