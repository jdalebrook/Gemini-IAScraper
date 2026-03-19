import os
import sqlite3
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "noticias_ia.db")
ESTADO_PATH = os.path.join(PROJECT_ROOT, "data", "processor.state")

# =========================================================
# 🎛️ PANEL DE CONTROL (AJUSTE SEGURO)
# =========================================================
MODO_PAGO = False          # False = gratis (AI Studio key) | True = de pago (Cloud key)
LIMITE_DIARIO_FREE = 100   # Máximo de noticias/día en modo gratuito (cuota segura)
LIMITE_DIARIO_PAID = 800   # Máximo de noticias/día en modo de pago
PRECIO_APROX_NOTICIA = 0.00012
# =========================================================

def get_estado():
    try:
        with open(ESTADO_PATH) as f:
            return f.read().strip()
    except FileNotFoundError:
        return "running"

def set_estado(estado):
    with open(ESTADO_PATH, "w") as f:
        f.write(estado)

_api_key = os.getenv("GEMINI_API_KEY_PAID") if MODO_PAGO else os.getenv("GEMINI_API_KEY_FREE")
if not _api_key:
    raise ValueError(f"Falta la variable {'GEMINI_API_KEY_PAID' if MODO_PAGO else 'GEMINI_API_KEY_FREE'} en el .env")
client = genai.Client(api_key=_api_key)

def obtener_stats_hoy():
    hoy = datetime.now().strftime('%Y-%m-%d')
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM noticias WHERE titular_es IS NOT NULL AND created_at >= ?', (hoy,))
            total = cursor.fetchone()[0]
            limite = LIMITE_DIARIO_PAID if MODO_PAGO else LIMITE_DIARIO_FREE
            coste = round(total * PRECIO_APROX_NOTICIA, 2) if MODO_PAGO else 0.0
            return total, coste, limite
    except:
        return 0, 0.0, LIMITE_DIARIO_PAID if MODO_PAGO else LIMITE_DIARIO_FREE

def procesar_con_gemini():
    procesadas_hoy, gasto_hoy, limite_hoy = obtener_stats_hoy()

    if MODO_PAGO:
        PAUSA, LOTE = 2, 20
        tipo_modo = "⚡ MODO PAGO"
        if procesadas_hoy >= LIMITE_DIARIO_PAID:
            print(f"🛑 LIMITE DE COSTE ALCANZADO ({procesadas_hoy}/{LIMITE_DIARIO_PAID}) — auto-pausando")
            set_estado("paused_cost")
            return "STOP"
    else:
        PAUSA, LOTE = 30, 5
        tipo_modo = "🛡️ MODO GRATIS"
        if procesadas_hoy >= LIMITE_DIARIO_FREE:
            print(f"🛑 TOPE DIARIO ALCANZADO ({procesadas_hoy}/{LIMITE_DIARIO_FREE}) — auto-pausando hasta mañana")
            set_estado("paused_limit")
            return "STOP"

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM noticias WHERE titular_es IS NULL ORDER BY id DESC LIMIT {LOTE}')
        filas = cursor.fetchall()

        if not filas:
            return False

        print(f"{tipo_modo} | Procesadas hoy: {procesadas_hoy}/{limite_hoy} | Gastado: {gasto_hoy}€ | Lote: {len(filas)}")

        for fila in filas:
            try:
                prompt = (
                    f"Analiza esta noticia de IA: {fila['titulo_original']}. "
                    "Responde estrictamente en JSON con este formato: "
                    "{'titular_es': 'Traducido al español profesional', "
                    "'resumen_es': 'Resumen en una frase', "
                    "'score': (1-10 siendo 10 ciencia probada y 1 rumor/clickbait), "
                    "'razon': 'Breve explicación del score'}"
                )

                response = client.models.generate_content(
                    model='gemini-2.5-flash-lite',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type='application/json',
                    ),
                )

                data = json.loads(response.text)

                cursor.execute('''
                    UPDATE noticias SET
                    titular_es=?, resumen_es=?, score_fiabilidad=?, analisis_objetivo=?
                    WHERE id=?
                ''', (
                    data.get('titular_es', 'Sin título'),
                    data.get('resumen_es', 'Sin resumen'),
                    data.get('score', 5),
                    data.get('razon', ''),
                    fila['id']
                ))
                conn.commit()

                print(f"  ✅ [{data.get('score')}/10] {data.get('titular_es')[:45]}...")
                time.sleep(PAUSA)

            except Exception as e:
                if "429" in str(e):
                    print("🛑 Cuota agotada temporalmente. Esperando 1 min...")
                    time.sleep(60)
                else:
                    print(f"⚠️ Error en noticia {fila['id']}: {e}")
                break
    return True

if __name__ == "__main__":
    print(f"--- INICIANDO PROCESADOR ---")
    set_estado("running")
    while True:
        try:
            estado = get_estado()
            if estado in ("paused", "paused_cost", "paused_limit"):
                print(f"⏸️  Pausado [{estado}]. Comprobando en 60s...")
                time.sleep(60)
                continue

            res = procesar_con_gemini()
            if res == "STOP":
                time.sleep(3600)
            elif not res:
                print("☕ Todo procesado. Esperando 10 min...")
                time.sleep(600)
        except KeyboardInterrupt:
            print("\n👋 Cerrando procesador...")
            set_estado("stopped")
            break
