import google.generativeai as genai
import sqlite3
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
DB_PATH = "noticias_ia.db"

def procesar_con_gemini():
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Procesamos en lotes de 10 para ver resultados rápido en la web
        cursor.execute('SELECT id, titulo_original, url FROM noticias WHERE titular_es IS NULL LIMIT 10')
        filas = cursor.fetchall()

        if not filas:
            return False # No hay nada que procesar

        print(f"🤖 [{datetime.now().strftime('%H:%M')}] Procesando lote de {len(filas)} noticias...")

        for id_noticia, titulo, url in filas:
            prompt = f"Analiza esta noticia tecnológica y responde en JSON: Título: {titulo}, URL: {url}. Estructura: titular_es, resumen_es, score, razon."

            try:
                response = model.generate_content(prompt)
                data = json.loads(response.text)

                cursor.execute('''
                    UPDATE noticias SET titular_es = ?, resumen_es = ?, score_fiabilidad = ?, analisis_objetivo = ?
                    WHERE id = ?
                ''', (data['titular_es'], data['resumen_es'], data['score'], data['razon'], id_noticia))
                conn.commit()

                print(f"✅ [{id_noticia}] {data['titular_es']}")
                time.sleep(20) # Margen de seguridad alto (3 RPM)

            except Exception as e:
                if "429" in str(e):
                    print("🛑 Cuota alcanzada. Enfriando 5 minutos...")
                    time.sleep(300)
                continue
    return True

if __name__ == "__main__":
    print("🚀 Procesador de IA en segundo plano iniciado...")
    while True:
        hubo_trabajo = procesar_con_gemini()
        if not hubo_trabajo:
            print("☕ Todo procesado. Reintentando en 10 minutos...")
            time.sleep(600)
        else:
            print("📦 Lote terminado. Continuando con el siguiente...")