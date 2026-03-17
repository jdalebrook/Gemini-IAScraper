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

# =========================================================
# 🎛️ PANEL DE CONTROL (AJUSTE SEGURO)
# =========================================================
MODO_PAGO = False          # False = 0€ | True = Rápido pero con coste
LIMITE_DIARIO = 800
PRECIO_APROX_NOTICIA = 0.00012
# =========================================================

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def obtener_stats_hoy():
    hoy = datetime.now().strftime('%Y-%m-%d')
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM noticias WHERE titular_es IS NOT NULL AND created_at >= ?', (hoy,))
            total = cursor.fetchone()[0]
            coste = round(total * PRECIO_APROX_NOTICIA, 2) if MODO_PAGO else 0.0
            return total, coste
    except:
        return 0, 0.0

def procesar_con_gemini():
    procesadas_hoy, gasto_hoy = obtener_stats_hoy()

    if MODO_PAGO:
        PAUSA, LOTE = 2, 20
        tipo_modo = "⚡ MODO PAGO"
        if procesadas_hoy >= LIMITE_DIARIO:
            print(f"🛑 LIMITE DIARIO ALCANZADO ({procesadas_hoy})")
            return "STOP"
    else:
        PAUSA, LOTE = 30, 5
        tipo_modo = "🛡️ MODO GRATIS"

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM noticias WHERE titular_es IS NULL ORDER BY id DESC LIMIT {LOTE}')
        filas = cursor.fetchall()

        if not filas:
            return False

        print(f"{tipo_modo} | Gastado hoy: {gasto_hoy}€ | Pendientes: {len(filas)}")

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
                    model='gemini-flash-latest',
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
    while True:
        try:
            res = procesar_con_gemini()
            if res == "STOP":
                time.sleep(3600)
            elif not res:
                print("☕ Todo procesado. Esperando 10 min...")
                time.sleep(600)
        except KeyboardInterrupt:
            print("\n👋 Cerrando procesador...")
            break
