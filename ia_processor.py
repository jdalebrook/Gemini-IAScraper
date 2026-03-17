import os
import sqlite3
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# =========================================================
# 🎛️ PANEL DE CONTROL (AJUSTE SEGURO)
# =========================================================
MODO_PAGO = False          # 🛡️ Cambia a False para COSTE 0€ GARANTIZADO
LIMITE_DIARIO = 800
PRECIO_APROX_NOTICIA = 0.00012
DB_PATH = "noticias_ia.db"
# =========================================================

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def obtener_stats_hoy():
    hoy = datetime.now().strftime('%Y-%m-%d')
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM noticias WHERE titular_es IS NOT NULL AND created_at >= ?', (hoy,))
            total = cursor.fetchone()[0]
            # Si estamos en modo gratis, el coste siempre se muestra como 0.0€
            coste = round(total * PRECIO_APROX_NOTICIA, 2) if MODO_PAGO else 0.0
            return total, coste
    except: return 0, 0.0

def procesar_con_gemini():
    procesadas_hoy, gasto_hoy = obtener_stats_hoy()

    # Configuración de seguridad según el interruptor
    if MODO_PAGO:
        PAUSA, LOTE = 2, 20
        tipo_modo = "⚡ MODO PAGO (CUIDADO)"
        if procesadas_hoy >= LIMITE_DIARIO:
            print(f"🛑 LIMITE DIARIO ALCANZADO ({procesadas_hoy})")
            return "STOP"
    else:
        # Forzamos lentitud para no salirnos nunca de la cuota free
        PAUSA, LOTE = 30, 5
        tipo_modo = "🛡️ MODO GRATIS (SEGURO)"

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM noticias WHERE titular_es IS NULL LIMIT {LOTE}')
        filas = cursor.fetchall()

        if not filas: return False

        print(f"{tipo_modo} | Gastado hoy: {gasto_hoy}€ | Procesando {len(filas)} noticias...")

        for fila in filas:
            try:
                # Usamos gemini-flash-latest: compatible con free y pago
                response = client.models.generate_content(
                    model='gemini-flash-latest',
                    contents=f"Analiza y responde en JSON. Noticia: {fila['titulo_original']}. JSON: {{'titular_es': '...', 'resumen_es': '...', 'score': 1-10, 'razon': '...'}}",
                    config=types.GenerateContentConfig(
                        response_mime_type='application/json',
                    ),
                )

                data = json.loads(response.text)

                titular = data.get('titular_es') or data.get('titular') or "Sin título"
                resumen = data.get('resumen_es') or data.get('resumen') or "Sin resumen"
                score = data.get('score') or 5
                razon = data.get('razon') or data.get('analisis') or ""

                cursor.execute('''
                    UPDATE noticias SET titular_es=?, resumen_es=?, score_fiabilidad=?, analisis_objetivo=?
                    WHERE id=?
                ''', (titular, resumen, score, razon, fila['id']))
                conn.commit()

                print(f"  ✅ {titular[:50]}...")
                time.sleep(PAUSA)

            except Exception as e:
                # Si estamos en modo gratis y Google nos frena por velocidad
                if "429" in str(e):
                    print("🛑 Límite de velocidad gratuito alcanzado. Esperando 1 minuto...")
                    time.sleep(60)
                else:
                    print(f"⚠️ Error: {e}")
                break
    return True

if __name__ == "__main__":
    print(f"--- INICIANDO PROCESADOR (MODO: {'PAGO' if MODO_PAGO else 'GRATIS'}) ---")
    while True:
        res = procesar_con_gemini()
        if res == "STOP":
            time.sleep(3600)
            continue
        if not res:
            print("☕ Sin noticias nuevas. Reintentando en 10 min...")
            time.sleep(600)